#!/usr/bin/env python3
"""
The Forge V5: Autonomous Constrained Reasoning System
Core Gatekeeper & Validation Engine

Implements:
- Phase 1: Pre-Plan Mode & Scope Hash Locking (Input Gate)
- Phase 2: Per-Language Native Execution & Partial Pass Intelligence
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# --- Phase 1: Scope Hash Locking ---

def generate_scope_hash(preplan_document: str) -> str:
    """Generate a SHA256 hash of the pre-plan document."""
    return hashlib.sha256(preplan_document.encode('utf-8')).hexdigest()

def verify_scope_lock(expected_hash: str, preplan_document: str) -> bool:
    """Verify that the scope hasn't silently drifted."""
    current_hash = generate_scope_hash(preplan_document)
    return current_hash == expected_hash

# --- Phase 2: Native Validation & Partial Pass Intelligence ---

class ForgeValidator:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.results = {
            "total_files": 0,
            "passed": 0,
            "failed": 0,
            "failure_rate": 0.0,
            "languages": defaultdict(lambda: {"passed": 0, "failed": 0, "errors": []})
        }
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.sh': 'bash',
            '.bash': 'bash',
            '.sol': 'solidity',
            '.yul': 'solidity'
        }

    def _get_files_by_language(self) -> Dict[str, List[Path]]:
        files_by_lang = defaultdict(list)
        for ext, lang in self.supported_extensions.items():
            for file in self.target_dir.rglob(f"*{ext}"):
                if '.git' in file.parts or 'node_modules' in file.parts or 'venv' in file.parts or '.venv' in file.parts:
                    continue
                if file.name.startswith('forge_test_arena_'):
                    continue
                files_by_lang[lang].append(file)
        return files_by_lang

    def _validate_python(self, files: List[Path]):
        for f in files:
            self.results["total_files"] += 1
            cmd = ["python3", "-m", "py_compile", str(f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.results["languages"]["python"]["passed"] += 1
                self.results["passed"] += 1
            else:
                self.results["languages"]["python"]["failed"] += 1
                self.results["languages"]["python"]["errors"].append({"file": str(f), "error": res.stderr.strip()})
                self.results["failed"] += 1

    def _validate_javascript(self, files: List[Path]):
        for f in files:
            self.results["total_files"] += 1
            cmd = ["node", "--check", str(f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.results["languages"]["javascript"]["passed"] += 1
                self.results["passed"] += 1
            else:
                self.results["languages"]["javascript"]["failed"] += 1
                self.results["languages"]["javascript"]["errors"].append({"file": str(f), "error": res.stderr.strip()})
                self.results["failed"] += 1

    def _validate_cpp(self, files: List[Path]):
        for f in files:
            self.results["total_files"] += 1
            cmd = ["g++", "-fsyntax-only", str(f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.results["languages"]["cpp"]["passed"] += 1
                self.results["passed"] += 1
            else:
                self.results["languages"]["cpp"]["failed"] += 1
                self.results["languages"]["cpp"]["errors"].append({"file": str(f), "error": res.stderr.strip()})
                self.results["failed"] += 1
                
    def _validate_bash(self, files: List[Path]):
        for f in files:
            self.results["total_files"] += 1
            cmd = ["bash", "-n", str(f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.results["languages"]["bash"]["passed"] += 1
                self.results["passed"] += 1
            else:
                self.results["languages"]["bash"]["failed"] += 1
                self.results["languages"]["bash"]["errors"].append({"file": str(f), "error": res.stderr.strip()})
                self.results["failed"] += 1

    def _validate_solidity(self, files: List[Path]):
        if not files:
            return

        self.results["total_files"] += len(files)
        cmd = ["forge", "build", "--root", str(self.target_dir)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            self.results["languages"]["solidity"]["passed"] += len(files)
            self.results["passed"] += len(files)
        else:
            self.results["languages"]["solidity"]["failed"] += len(files)
            self.results["languages"]["solidity"]["errors"].append({
                "file": str(self.target_dir),
                "error": (res.stderr.strip() or res.stdout.strip() or "forge build failed")[:4000],
            })
            self.results["failed"] += len(files)

    def _validate_ruby(self, files: List[Path]):
        for f in files:
            self.results["total_files"] += 1
            cmd = ["ruby", "-c", str(f)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.results["languages"]["ruby"]["passed"] += 1
                self.results["passed"] += 1
            else:
                self.results["languages"]["ruby"]["failed"] += 1
                self.results["languages"]["ruby"]["errors"].append({"file": str(f), "error": res.stderr.strip()})
                self.results["failed"] += 1

    def run_validation(self) -> Dict:
        files_by_lang = self._get_files_by_language()
        
        if "python" in files_by_lang:
            self._validate_python(files_by_lang["python"])
        if "javascript" in files_by_lang:
            self._validate_javascript(files_by_lang["javascript"])
        if "cpp" in files_by_lang:
            self._validate_cpp(files_by_lang["cpp"])
        if "bash" in files_by_lang:
            self._validate_bash(files_by_lang["bash"])
        if "solidity" in files_by_lang:
            self._validate_solidity(files_by_lang["solidity"])
        if "ruby" in files_by_lang:
            self._validate_ruby(files_by_lang["ruby"])
            
        # TODO: Add rust, go, java when cargo/go toolchains are confirmed present in the module root.
            
        if self.results["total_files"] > 0:
            self.results["failure_rate"] = round(self.results["failed"] / self.results["total_files"], 4)
            
        return self.results

    def validate_code_blocks(self, text: str) -> Dict:
        import tempfile
        import re
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract code blocks with language specifiers
            pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
            matches = pattern.findall(text)
            
            # Map common block languages to extensions
            ext_map = {"python": ".py", "javascript": ".js", "js": ".js", "cpp": ".cpp", "c": ".c", "bash": ".sh", "sh": ".sh", "ruby": ".rb"}
            
            for i, (lang, code) in enumerate(matches):
                lang = lang.lower().strip()
                if lang in ext_map:
                    ext = ext_map[lang]
                    file_path = Path(tmpdir) / f"block_{i}{ext}"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(code)
            
            # Save current target, temporarily override, and run validation
            original_dir = self.target_dir
            self.target_dir = Path(tmpdir)
            self.results = {
                "total_files": 0, "passed": 0, "failed": 0, "failure_rate": 0.0,
                "languages": defaultdict(lambda: {"passed": 0, "failed": 0, "errors": []})
            }
            res = self.run_validation()
            self.target_dir = original_dir
            return res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: forge_v5_gatekeeper.py <target_directory>")
        sys.exit(1)
        
    target = sys.argv[1]
    print(f"🔥 INITIALIZING FORGE V5 GATEKEEPER ON: {target}")
    
    validator = ForgeValidator(target)
    report = validator.run_validation()
    
    print("\n📊 PARTIAL PASS INTELLIGENCE REPORT:")
    print(json.dumps(report, indent=2))
    
    if report["failed"] > 0:
        sys.exit(1)
    sys.exit(0)
