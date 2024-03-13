import subprocess

def llmcall(query, m13=False):
    model="-m13 " if m13 else ""
    res=subprocess.run(f"llm {model}{query}", capture_output=True)
    return res.stdout.decode()
