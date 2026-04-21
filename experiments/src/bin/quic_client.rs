use anyhow::{Context, Result};
use clap::Parser;
use quinn::{ClientConfig, Endpoint};
use rustls::RootCertStore;
use std::{
    collections::HashMap,
    fs::File,
    io::BufReader,
    net::SocketAddr,
    sync::{Arc, Mutex},
    time::{Duration, SystemTime, UNIX_EPOCH},
};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader as TokioBufReader};

#[derive(Parser, Debug)]
struct Args {
    #[arg(long, default_value = "0.0.0.0:0")]
    bind: SocketAddr,

    #[arg(long, default_value = "10.0.3.2:4433")]
    server_addr: SocketAddr,

    #[arg(long, default_value = "server")]
    server_name: String,

    #[arg(long, default_value = "certs/cert.pem")]
    ca_cert: String,

    #[arg(long, default_value_t = 100)]
    interval_ms: u64,
}

fn load_roots(path: &str) -> Result<Arc<RootCertStore>> {
    let f = File::open(path).with_context(|| format!("open CA cert file: {path}"))?;
    let mut reader = BufReader::new(f);
    let certs = rustls_pemfile::certs(&mut reader)
        .collect::<std::result::Result<Vec<_>, _>>()
        .context("parse CA certificate PEM")?;

    let mut roots = RootCertStore::empty();
    for cert in certs {
        roots.add(cert).context("add CA cert to root store")?;
    }
    Ok(Arc::new(roots))
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis()
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();

    let roots = load_roots(&args.ca_cert)?;
    let client_config =
        ClientConfig::with_root_certificates(roots).context("build ClientConfig")?;

    let mut endpoint = Endpoint::client(args.bind).context("bind QUIC client")?;
    endpoint.set_default_client_config(client_config);

    let conn = endpoint
        .connect(args.server_addr, &args.server_name)
        .context("start QUIC connect")?
        .await
        .context("finish QUIC connect")?;

    println!(
        "QUIC_CLIENT_CONNECTED stable_id={} remote={}",
        conn.stable_id(),
        conn.remote_address()
    );

    let (mut send, recv) = conn.open_bi().await.context("open_bi failed")?;

    // Important for Quinn: server-side accept_bi won't see the stream until the opener writes.
    send.write_all(b"HELLO\n").await.context("initial write failed")?;
    send.flush().await.context("initial flush failed")?;

    let sent_times: Arc<Mutex<HashMap<u64, u128>>> = Arc::new(Mutex::new(HashMap::new()));

    let recv_sent_times = sent_times.clone();
    let recv_conn = conn.clone();
    tokio::spawn(async move {
        let mut reader = TokioBufReader::new(recv);
        let mut line = String::new();

        loop {
            line.clear();
            match reader.read_line(&mut line).await {
                Ok(0) => {
                    eprintln!("QUIC_RECV_EOF");
                    break;
                }
                Ok(_) => {
                    let line_trim = line.trim();
                    if line_trim == "HELLO" {
                        continue;
                    }

                    let parts: Vec<&str> = line_trim.split(',').collect();
                    if parts.len() != 2 {
                        eprintln!("QUIC_BAD_ECHO {}", line_trim);
                        continue;
                    }

                    let seq: u64 = match parts[0].parse() {
                        Ok(v) => v,
                        Err(e) => {
                            eprintln!("QUIC_BAD_SEQ {} ({e})", line_trim);
                            continue;
                        }
                    };
                    let send_ms: u128 = match parts[1].parse() {
                        Ok(v) => v,
                        Err(e) => {
                            eprintln!("QUIC_BAD_TS {} ({e})", line_trim);
                            continue;
                        }
                    };

                    let now = now_ms();
                    let rtt_app = now.saturating_sub(send_ms);

                    println!(
                        "QUIC_ECHO seq={} send_ms={} recv_ms={} app_rtt_ms={} remote={} quinn_rtt_ms={}",
                        seq,
                        send_ms,
                        now,
                        rtt_app,
                        recv_conn.remote_address(),
                        recv_conn.rtt().as_millis()
                    );

                    recv_sent_times.lock().unwrap().remove(&seq);
                }
                Err(e) => {
                    eprintln!("QUIC_RECV_ERROR {e:#}");
                    break;
                }
            }
        }
    });

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

    let mut seq: u64 = 0;
    let interval = Duration::from_millis(args.interval_ms);

    loop {
        let t = now_ms();
        let msg = format!("{seq},{t}\n");
        sent_times.lock().unwrap().insert(seq, t);

        if let Err(e) = send.write_all(msg.as_bytes()).await {
            eprintln!("QUIC_SEND_ERROR seq={} err={:#}", seq, e);
            break;
        }
        if let Err(e) = send.flush().await {
            eprintln!("QUIC_FLUSH_ERROR seq={} err={:#}", seq, e);
            break;
        }

        println!("QUIC_TX seq={} send_ms={}", seq, t);
        seq += 1;
        tokio::time::sleep(interval).await;
    }

    Ok(())
}