#!/bin/bash
# THE FORGE (A.F.P) - 5 Minute Setup
# "Most AI passes tests. Very few survive the Forge."

echo "🔥 INITIALIZING THE FORGE (A.F.P) PROTOCOL..."

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found. Please install it first."
    exit 1
fi

# 2. Virtual Environment (Isolation for Safety)
if [ ! -d "venv" ]; then
    echo "📦 Creating secure environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Fast Dependency Install
echo "🛠️ Hardening dependencies..."
pip install --quiet --upgrade pip
pip install --quiet requests numpy scipy sentence-transformers torch

# 4. Create local results directory
mkdir -p enhanced_harness_results

echo "✅ THE FORGE IS READY."
echo "🚀 Run 'bash run.sh' to initiate the protocol."
