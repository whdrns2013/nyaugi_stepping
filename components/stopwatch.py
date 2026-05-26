import streamlit as st
import time
import tempfile

def _format_ms(ms):
    total_seconds = int(ms) // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    millis = int(ms) % 1000
    return f"{minutes:02d}:{seconds:02d}.{millis:03d}"

def _build_html_running(start_time_ts):
    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    padding: 20px;
    font-family: 'Segoe UI', Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: transparent;
    overflow: hidden;
  }}
  .display {{
    font-size: clamp(36px, 10vw, 72px);
    font-family: 'Consolas', 'Courier New', monospace;
    font-weight: bold;
    color: #2ecc71;
    background-color: #1a1a2e;
    padding: 20px;
    border-radius: 12px;
    letter-spacing: 2px;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }}
</style>
</head>
<body>
  <div class="display" id="display"></div>
<script>
  const startTs = {start_time_ts};
  function formatTime(ms) {{
    const totalMs = Math.floor(ms);
    const totalSeconds = Math.floor(totalMs / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const millis = totalMs % 1000;
    return String(minutes).padStart(2, '0') + ':' +
           String(seconds).padStart(2, '0') + '.' +
           String(millis).padStart(3, '0');
  }}
  function tick() {{
    const elapsed = Date.now() - startTs;
    document.getElementById('display').textContent = formatTime(elapsed);
    requestAnimationFrame(tick);
  }}
  tick();
</script>
</body>
</html>
"""

def _build_html_static(formatted_time, color="#ffffff"):
    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    padding: 20px;
    font-family: 'Segoe UI', Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: transparent;
    overflow: hidden;
  }}
  .display {{
    font-size: clamp(36px, 10vw, 72px);
    font-family: 'Consolas', 'Courier New', monospace;
    font-weight: bold;
    color: {color};
    background-color: #1a1a2e;
    padding: 20px;
    border-radius: 12px;
    letter-spacing: 2px;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }}
</style>
</head>
<body>
  <div class="display">{formatted_time}</div>
</body>
</html>
"""

def _write_html_file(html_content):
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8'
    )
    tmp.write(html_content)
    tmp.close()
    return tmp.name

def render_stopwatch(state, start_time):
    """
    스탑워치를 렌더링하고 경과 시간을 ms 단위로 반환.
    state: "running" | "stopped" | "idle"
    start_time: datetime 객체 (시작 시각), idle 시 None
    """
    if state == "idle":
        html = _build_html_static("00:00.000", color="#888888")
        filepath = _write_html_file(html)
        st.iframe(filepath, height=180)
        return 0

    elif state == "running" and start_time is not None:
        start_ts_ms = int(start_time.timestamp() * 1000)
        html = _build_html_running(start_ts_ms)
        filepath = _write_html_file(html)
        st.iframe(filepath, height=180)
        now_ts = time.time()
        elapsed_ms = (now_ts - start_time.timestamp()) * 1000
        return elapsed_ms

    elif state == "stopped":
        elapsed_ms = st.session_state.get("stopwatch_elapsed_ms", 0)
        formatted = _format_ms(elapsed_ms)
        html = _build_html_static(formatted, color="#e74c3c")
        filepath = _write_html_file(html)
        st.iframe(filepath, height=180)
        return elapsed_ms

    return 0
