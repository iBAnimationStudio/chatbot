use rusqlite::Connection;
use serde::{Serialize, Deserialize};
use std::env;

#[derive(Serialize, Deserialize)]
struct MemoryItem {
    id: i32,
    content: String,
    importance: f32,
    score: f32,
}

fn cosine(a: &[f32], b: &[f32]) -> f32 {
    let mut dot = 0.0;
    let mut na = 0.0;
    let mut nb = 0.0;

    for (x, y) in a.iter().zip(b.iter()) {
        dot += x * y;
        na += x * x;
        nb += y * y;
    }

    if na == 0.0 || nb == 0.0 {
        return 0.0;
    }

    dot / (na.sqrt() * nb.sqrt())
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 6 {
        eprintln!("Usage: search <vec> <limit> <db_path> <threshold>");
        return;
    }

    let query: Vec<f32> = serde_json::from_str(&args[2]).unwrap_or_default();
    let limit: usize = args[3].parse().unwrap_or(3);
    let db_path = &args[4];
    let threshold: f32 = args[5].parse().unwrap_or(0.6);

    let conn = match Connection::open(db_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("DB error: {}", e);
            return;
        }
    };

    let mut stmt = conn.prepare(
        "SELECT id, content, embedding, importance FROM memory"
    ).unwrap();

    let mut results = Vec::new();

    let rows = stmt.query_map([], |row| {
        Ok((
            row.get::<_, i32>(0)?,
            row.get::<_, String>(1)?,
            row.get::<_, String>(2)?,
            row.get::<_, f32>(3)?,
        ))
    }).unwrap();

    for row in rows {
        let (id, content, emb_str, importance) = match row {
            Ok(v) => v,
            Err(_) => continue,
        };

        let emb: Vec<f32> = match serde_json::from_str(&emb_str) {
            Ok(v) => v,
            Err(_) => continue,
        };

        if emb.len() != query.len() {
            continue;
        }

        let sim = cosine(&query, &emb);

        if sim < threshold {
            continue;
        }

        let score = (sim * 0.7) + (importance * 0.3);

        results.push(MemoryItem {
            id,
            content,
            importance,
            score,
        });
    }

    results.sort_by(|a, b| {
        b.score.partial_cmp(&a.score).unwrap()
    });

    results.truncate(limit);

    println!("{}", serde_json::to_string(&results).unwrap());
}