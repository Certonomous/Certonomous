# Certonomous on your laptop — the backup

**Read the first two lines and you know what this is.**

This runs the **closure-challenge page and the four recorded acts** on your
laptop, with no internet and no EC2 box. It is your safety net if the box is
down or the wifi is bad.

It **cannot run a new act**. The acts need CFD solvers that are not on your
laptop. Detail in "Why it replays" at the bottom — but the short version is:
plan to shoot from the lab box, and keep this in your back pocket.

---

## 1. Install Python (once, before the shoot)

Go to **https://www.python.org/downloads/windows/** and get the latest
**Windows installer (64-bit)** — Python 3.12 or 3.13 is ideal, anything 3.10
or newer works.

In the installer, **tick "Add python.exe to PATH"** on the first screen. That
one checkbox is the only thing that goes wrong here.

Nothing else to install. No pip, no packages.

## 2. Extract

Right-click `certonomous-demo.zip` → **Extract All**. Anywhere is fine;
your Desktop is fine.

## 3. Run it

**Use Git Bash.** Right-click inside the extracted `certonomous-demo` folder
→ **Open Git Bash here**, then:

```bash
bash run-demo.sh
```

That is the whole thing. Your browser opens by itself.

<details>
<summary>PowerShell instead</summary>

```powershell
python replay_console.py
```

Use that rather than `.\run-demo.ps1` — it does exactly the same job and
never trips over PowerShell's script-execution policy.
</details>

## 4. Confirm it is working

You should see:

```
  CERTONOMOUS -- offline laptop console
  Control room (replays)  http://localhost:8765
  Static site             http://localhost:8080/closure.html
  Recorded missions ready 4
```

The control room opens in your browser and the four acts are listed. Click
one and it replays — transcript, plots, verdict, certificate.

**The closure page** — the one you talk over — is at
**http://localhost:8080/closure.html**

To stop it: click the black window and press **Ctrl+C**.

## 5. If something goes wrong

**"Could not find Python 3.10 or newer"**
The PATH checkbox was missed. Re-run the Python installer, choose **Modify**,
and tick "Add python.exe to PATH". Then close the window, open a new one,
and run it again.

**A port is already in use**
Nothing to do — it moves up on its own and prints the port it actually used.
Read the URLs off the black window rather than typing 8765 from memory.

**The browser did not open**
Type the URL from the black window in yourself.

**The page is blank or stale**
Hard-refresh: **Ctrl+Shift+R**.

---

## Why it replays instead of running live

Measured on 2026-07-30 by tracing every process the four acts spawn:

- The **airliner** and **Monte Carlo race** acts run the real **VSPAERO**
  binary — 102 times between them. Those are live solves.
- The **NASA hump** and **B-52** acts run OpenFOAM utilities and **compile
  C++ while the act is running** (OpenFOAM's dynamic-code path).

None of that exists on a Windows laptop, and it is not something to install
the night before a shoot. So the console serves what the real runs produced,
and says plainly that it is a replay. The numbers are the numbers those runs
measured — nothing here is a mock-up, and nothing is dressed up as live.

The lab-credentials wall and the header counts (208,102 evaluations, 239.3
core-hours) are a snapshot taken when this bundle was built, so they read
exactly what the lab box reads.
