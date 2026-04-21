use anyhow::{Context, Result};
use clap::Parser;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::TcpStream,
};

#[derive(Parser, Debug)]
struct Args {
    #[arg(long, default_value = "10.0.3.2:5000")]
    server_addr: String,

    #[arg(long, default_value_t = 100)]
    interval_ms: u64,
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis()
}

#[tokio::main]
async fn main() -> Result<()> {
    let stream = TcpStream::connect(&args().server_addr)
        .await
        .context("connect TCP failed")?;
    let peer = stream.peer_addr().context("peer_addr failed")?;
    println!("TCP_CLIENT_CONNECTED peer={peer}");

    let (reader_half, mut writer_half) = stream.into_split();

    tokio::spawn(async move {
        let mut reader = BufReader::new(reader_half);
        let mut line = String::new();
        loop {
            line.clear();
            match reader.read_line(&mut line).await {
                Ok(0) => {
                    eprintln!("TCP_RECV_EOF");
                    break;
                }
                Ok(_) => {
                    let line_trim = line.trim();
                    let parts: Vec<&str> = line_trim.split(',').collect();
                    if parts.len() == 2 {
                        if let (Ok(seq), Ok(send_ms)) =
                            (parts[0].parse::<u64>(), parts[1].parse::<u128>())
                        {
                            let now = now_ms();
                            println!(
                                "TCP_ECHO seq={} send_ms={} recv_ms={} app_rtt_ms={}",
                                seq,
                                send_ms,
                                now,
                                now.saturating_sub(send_ms)
                            );
                        }
                    }
                }
                Err(e) => {
                    eprintln!("TCP_RECV_ERROR {e:#}");
                    break;
                }
            }
        }
    });

    let mut seq: u64 = 0;
    let interval = Duration::from_millis(args().interval_ms);

    loop {
        let t = now_ms();
        let msg = format!("{seq},{t}\n");
        if let Err(e) = writer_half.write_all(msg.as_bytes()).await {
            eprintln!("TCP_SEND_ERROR seq={} err={:#}", seq, e);
            break;
        }
        if let Err(e) = writer_half.flush().await {
            eprintln!("TCP_FLUSH_ERROR seq={} err={:#}", seq, e);
            break;
        }

        println!("TCP_TX seq={} send_ms={}", seq, t);
        seq += 1;
        tokio::time::sleep(interval).await;
    }

    Ok(())
}

fn args() -> Args {
    use std::sync::OnceLock;
    static ARGS: OnceLock<Args> = OnceLock::new();
    ARGS.get_or_init(Args::parse).clone()
}

impl Clone for Args {
    fn clone(&self) -> Self {
        Self {
            server_addr: self.server_addr.clone(),
            interval_ms: self.interval_ms,
        }
    }
}