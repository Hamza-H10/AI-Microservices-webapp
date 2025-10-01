import argparse
import time
from transformers import pipeline
import torch


def bench(model_name: str, n: int, batch_size: int):
    print(f"Torch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        try:
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        except Exception:
            pass

    # Prepare inputs (repeat a few different sentences)
    seeds = [
        "I love using Hugging Face Transformers!",
        "The food at the restaurant was terrible.",
        "This movie was a bit boring.",
        "The concert was absolutely fantastic.",
    ]
    texts = [seeds[i % len(seeds)] for i in range(n)]

    # CPU pipeline
    print("\n[CPU] Loading pipeline…")
    clf_cpu = pipeline("sentiment-analysis", model=model_name, device=-1)
    _ = clf_cpu(["warmup"])  # warmup
    t0 = time.perf_counter()
    _ = clf_cpu(texts, batch_size=batch_size, truncation=True)
    t1 = time.perf_counter()
    cpu_s = t1 - t0
    print(f"[CPU] {n} texts, batch_size={batch_size}: {cpu_s:.3f}s")

    # GPU pipeline (if available)
    gpu_s = None
    if torch.cuda.is_available():
        print("\n[GPU] Loading pipeline…")
        clf_gpu = pipeline("sentiment-analysis", model=model_name, device=0)
        _ = clf_gpu(["warmup"])  # warmup to init kernels
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        _ = clf_gpu(texts, batch_size=batch_size, truncation=True)
        torch.cuda.synchronize()
        t1 = time.perf_counter()
        gpu_s = t1 - t0
        print(f"[GPU] {n} texts, batch_size={batch_size}: {gpu_s:.3f}s")

    if gpu_s is not None:
        speedup = cpu_s / gpu_s if gpu_s > 0 else float("inf")
        print(f"\nSpeedup (CPU/GPU): {speedup:.2f}x")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Quick CPU vs GPU benchmark for sentiment analysis")
    p.add_argument(
        "--model", default="distilbert-base-uncased-finetuned-sst-2-english", help="HF model id")
    p.add_argument("--n", type=int, default=256,
                   help="Number of input texts to process")
    p.add_argument("--batch-size", type=int, default=16,
                   help="Batch size for pipeline calls")
    args = p.parse_args()

    bench(args.model, args.n, args.batch_size)
