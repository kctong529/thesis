use anyhow::{anyhow, Context, Result};
use clap::Parser;
use quinn::{Endpoint, Incoming, ServerConfig};
use std::{fs::File, io::BufReader, net::SocketAddr, sync::Arc, time::Duration};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader as TokioBufReader};

#[derive(Parser, Debug)]
struct Args {
    #[arg(long, default_value = "0.0.0.0:4433")]
    bind: SocketAddr,

    #[arg(long, default_value = "certs/cert.pem")]
    cert: String,

    #[arg(long, default_value = "certs/key.pem")]
    key: String,
}

fn load_certs(path: &str) -> Result<Vec<rustls::pki_types::CertificateDer<'static>>> {
    let f = File::open(path).with_context(|| format!("open cert file: {path}"))?;
    let mut reader = BufReader::new(f);
    let certs = rustls_pemfile::certs(&mut reader)
        .collect::<std::result::Result<Vec<_>, _>>()
        .context("parse certificate PEM")?;
    Ok(certs)
}

fn load_key(path: &str) -> Result<rustls::pki_types::PrivateKeyDer<'static>> {
    let f = File::open(path).with_context(|| format!("open key file: {path}"))?;
    let mut reader = BufReader::new(f);
    let key = rustls_pemfile::private_key(&mut reader)
        .context("parse private key PEM")?
        .ok_or_else(|| anyhow!("no private key found in {path}"))?;
    Ok(key)
}

async fn handle_incoming(incoming: Incoming) -> Result<()> {
    let connecting = incoming.accept().context("incoming.accept() failed")?;
    let conn = connecting.await.context("QUIC handshake failed")?;

    println!(
        "QUIC_CONNECTED stable_id={} remote={}",
        conn.stable_id(),
        conn.remote_address()
    );

    let stats_conn = conn.clone();
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(Duration::from_secs(1)).await;
            println!(
                "QUIC_STATS stable_id={} remote={} rtt_ms={} stats={:?}",
                stats_conn.stable_id(),
                stats_conn.remote_address(),
                stats_conn.rtt().as_millis(),
                stats_conn.stats()
            );
        }
    });

    loop {
        let (mut send, recv) = conn.accept_bi().await.context("accept_bi failed")?;
        let mut reader = TokioBufReader::new(recv);
        let mut line = String::new();

        loop {
            line.clear();
            let n = reader.read_line(&mut line).await.context("read_line failed")?;
            if n == 0 {
                break;
            }

            print!("SERVER_RX {}", line);
            send.write_all(line.as_bytes()).await.context("echo write failed")?;
            send.flush().await.context("echo flush failed")?;
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    let certs = load_certs(&args.cert)?;
    let key = load_key(&args.key)?;

    let mut server_config =
        ServerConfig::with_single_cert(certs, key).context("build ServerConfig")?;

    // In current Quinn releases, migration is enabled by default.
    // If your exact version exposes this method, you may uncomment it:
    // server_config.migration(true);

    let endpoint = Endpoint::server(server_config, args.bind).context("bind QUIC server")?;
    println!("QUIC_SERVER_LISTEN {}", args.bind);

    loop {
        let Some(incoming) = endpoint.accept().await else {
            break;
        };
        tokio::spawn(async move {
            if let Err(e) = handle_incoming(incoming).await {
                eprintln!("SERVER_CONN_ERROR: {e:#}");
            }
        });
    }

    Ok(())
}