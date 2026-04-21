use anyhow::{Context, Result};
use clap::Parser;
use std::net::SocketAddr;
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{TcpListener, TcpStream},
};

#[derive(Parser, Debug)]
struct Args {
    #[arg(long, default_value = "0.0.0.0:5000")]
    bind: SocketAddr,
}

async fn handle_conn(stream: TcpStream) -> Result<()> {
    let peer = stream.peer_addr().context("peer_addr failed")?;
    println!("TCP_CONNECTED peer={peer}");

    let (reader_half, mut writer_half) = stream.into_split();
    let mut reader = BufReader::new(reader_half);
    let mut line = String::new();

    loop {
        line.clear();
        let n = reader.read_line(&mut line).await.context("TCP read_line failed")?;
        if n == 0 {
            println!("TCP_EOF peer={peer}");
            break;
        }

        print!("TCP_SERVER_RX {}", line);
        writer_half
            .write_all(line.as_bytes())
            .await
            .context("TCP echo write failed")?;
        writer_half.flush().await.context("TCP echo flush failed")?;
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    let listener = TcpListener::bind(args.bind).await.context("bind TCP server")?;
    println!("TCP_SERVER_LISTEN {}", args.bind);

    loop {
        let (stream, _) = listener.accept().await.context("accept TCP failed")?;
        tokio::spawn(async move {
            if let Err(e) = handle_conn(stream).await {
                eprintln!("TCP_CONN_ERROR: {e:#}");
            }
        });
    }
}