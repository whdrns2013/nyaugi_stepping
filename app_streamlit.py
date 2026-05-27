import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from services.history_crud import create_step_history, retrieve_all_history, retrieve_history_by_user_id, delete_step_history, retrieve_all_history_with_user_name, retrieve_history_by_user_name, update_step_history, create_step_history_from_csv
from services.user_crud import retrieve_all_users, retrieve_user_info_by_name
from schemas.step_history import CreateStepHistoryRequestBody, DeleteStepHistoryRequestBody, UpdateStepHistoryRequestBody
from schemas.users import CreateUserRequestBody
from config.enums import StatusCode
from components.stopwatch import render_stopwatch
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Nyaugi Stepping", layout="wide")

menus = ["리더보드", "계단오르기 시작", "이력 조회", "이력 시각화", "사용자 조회", "기록 등록", "기록 수정"]
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = menus[0]

st.title("Nyaugi Stepping - 계단 오르기 기록 관리")

# Sidebar Navigation
menu = st.sidebar.selectbox("메뉴 선택", menus, index=menus.index(st.session_state.selected_menu) if st.session_state.selected_menu in menus else 0, key="menu_select")
st.session_state.selected_menu = menu

if menu == "계단오르기 시작":
    st.header("🏃 계단오르기 시작")

    # session_state 초기화
    if "stopwatch_state" not in st.session_state:
        st.session_state.stopwatch_state = "idle"
    if "stopwatch_start_ts" not in st.session_state:
        st.session_state.stopwatch_start_ts = None
    if "stopwatch_elapsed_ms" not in st.session_state:
        st.session_state.stopwatch_elapsed_ms = 0
    if "stopwatch_perf_offset" not in st.session_state:
        st.session_state.stopwatch_perf_offset = 0

    # 버튼 컨트롤
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if st.button("시작 / 재시작", type="primary", use_container_width=True, key="sw_start"):
            st.session_state.stopwatch_state = "running"
            st.session_state.stopwatch_start_ts = datetime.now(ZoneInfo("Asia/Seoul"))
            st.session_state.stopwatch_perf_offset = time.time()
    with btn_col2:
        if st.button("중지", use_container_width=True, key="sw_stop"):
            if st.session_state.stopwatch_state == "running":
                st.session_state.stopwatch_state = "stopped"
                now_ts = time.time()
                offset = st.session_state.stopwatch_perf_offset
                elapsed_ms = int((now_ts - st.session_state.stopwatch_start_ts.timestamp()) * 1000)
                st.session_state.stopwatch_elapsed_ms = elapsed_ms
    with btn_col3:
        if st.button("초기화", use_container_width=True, key="sw_reset"):
            st.session_state.stopwatch_state = "idle"
            st.session_state.stopwatch_start_ts = None
            st.session_state.stopwatch_elapsed_ms = 0
            st.session_state.stopwatch_perf_offset = 0

    # 상태 표시
    state_map = {"idle": "⏸ 대기중", "running": "▶️ 계단오르기 진행중...", "stopped": "⏹ 중지됨"}
    st.caption(state_map.get(st.session_state.stopwatch_state, ""))

    # 스탑워치 시각화 렌더링 (실시간)
    elapsed_ms = render_stopwatch(
        st.session_state.stopwatch_state,
        st.session_state.stopwatch_start_ts
    )

    # 중지 후 기록 등록 폼
    if st.session_state.stopwatch_state == "stopped":
        st.subheader("📝 기록 등록")
        elapsed_ms = st.session_state.stopwatch_elapsed_ms
        elapsed_seconds = elapsed_ms / 1000
        st.caption(f'시작일시 : {st.session_state.stopwatch_start_ts.strftime("%Y-%m-%d %H:%M:%S.%f")}')
        st.caption(f"측정된 시간: {elapsed_seconds:.3f}초")

        # 사용자 목록 조회
        try:
            user_resp = retrieve_all_users()
            if user_resp.status_code == StatusCode.SUCCESS.value and user_resp.user_list:
                user_options = {f"{u.name} (email: {u.email})": u.id for u in user_resp.user_list}
                selected_user_label = st.selectbox("사용자 선택", options=list(user_options.keys()), key="sw_user_select")
                selected_user_id = user_options[selected_user_label]
            else:
                st.warning("등록된 사용자가 없습니다. 먼저 사용자를 등록해주세요.")
                selected_user_id = None
        except Exception as e:
            st.error(f"사용자 조회 중 오류 발생: {e}")
            selected_user_id = None

        with st.form("stopwatch_record_form"):
            col1, col2 = st.columns(2)
            with col1:
                sw_level = st.number_input("오른 층수", min_value=0, step=1, key="sw_level")
                sw_rest_count = st.number_input("휴식 횟수", min_value=0, step=1, key="sw_rest_count")
            with col2:
                sw_heartbeat = st.number_input("평균 심박수", min_value=0.0, step=0.1, key="sw_heartbeat")
                sw_rest_level_str = st.text_input("휴식 층수 (쉼표로 구분)", placeholder="5, 10, 15", key="sw_rest_level")

            sw_submit = st.form_submit_button("기록 저장", type="primary")

            if sw_submit:
                if selected_user_id is None:
                    st.error("사용자를 선택해주세요.")
                else:
                    try:
                        start_dt = st.session_state.stopwatch_start_ts
                        if start_dt is None:
                            st.error("스탑워치 시작 시간을 찾을 수 없습니다.")
                        else:
                            start_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
                            end_dt = start_dt + timedelta(milliseconds=elapsed_ms)
                            end_dt_str = end_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
                            duration = int(elapsed_seconds)

                            r_levels = None
                            if sw_rest_level_str:
                                r_levels = [int(x.strip()) for x in sw_rest_level_str.split(",") if x.strip()]

                            body = CreateStepHistoryRequestBody(
                                user_id=[selected_user_id],
                                start_datetime=start_dt_str,
                                end_datetime=end_dt_str,
                                level=sw_level,
                                rest_count=sw_rest_count if sw_rest_count else 0,
                                rest_level=r_levels,
                                heartbeat=sw_heartbeat if sw_heartbeat else 0
                            )

                            response = create_step_history(body)
                            if response.status_code == StatusCode.SUCCESS.value:
                                st.success("기록이 성공적으로 저장되었습니다!")
                                st.session_state.stopwatch_state = "idle"
                                st.session_state.stopwatch_start_ts = None
                                st.session_state.stopwatch_elapsed_ms = 0
                            else:
                                st.error(f"저장 실패: {response.message}")
                    except ValueError as e:
                        st.error(f"입력 형식이 잘못되었습니다: {e}")
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

elif menu == "리더보드":
    st.header("🏆 리더보드")
    
    try:
        response = retrieve_all_history_with_user_name()
        if response.status_code != StatusCode.SUCCESS.value:
            st.error(f"오류 발생: {response.message}")
        elif not response.history_list:
            st.info("리더보드를 위한 데이터가 없습니다.")
        else:
            data = []
            for h in response.history_list:
                if h.level and h.level > 0:
                    data.append({
                        "id": h.id,
                        "user_id": h.user_id,
                        "name": h.name,
                        "start_datetime": h.start_datetime,
                        "duration": h.duration,
                        "level": h.level,
                        "heartbeat": h.heartbeat if h.heartbeat else 0,
                    })
            df = pd.DataFrame(data)
            
            tabs = st.tabs(["누적 층수", "층당 소요시간", "최고 층수"])
            
            medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
            
            with tabs[0]:
                st.subheader("누적 층수 (사용자별)")
                user_agg = df.groupby("name").agg(
                    **{"누적 층수": ("level", "sum"), "기록 수": ("id", "count")}
                ).reset_index()
                user_agg = user_agg.sort_values("누적 층수", ascending=False).reset_index(drop=True)
                user_agg["등수"] = range(1, len(user_agg) + 1)
                user_agg["rank_display"] = user_agg["등수"].apply(
                    lambda r: medal_map.get(r, str(r))
                )
                user_agg["등수"] = user_agg["rank_display"]
                display_df = user_agg.rename(columns={"name": "사용자"})
                display_df = display_df[["등수", "사용자", "누적 층수", "기록 수"]]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            with tabs[1]:
                st.subheader("층당 소요시간 (이력별)")
                record_df = df.copy()
                try:
                    duration_per_level = (record_df["duration"] / record_df["level"]).round(1)
                except:
                    duration_per_level = 9999
                record_df["층당 소요(초)"] = duration_per_level
                record_df["날짜"] = record_df["start_datetime"].str[:10]
                record_df = record_df.sort_values("층당 소요(초)", ascending=True).reset_index(drop=True)
                record_df["등수"] = range(1, len(record_df) + 1)
                record_df["rank_display"] = record_df["등수"].apply(
                    lambda r: medal_map.get(r, str(r))
                )
                record_df["등수"] = record_df["rank_display"]
                display_df = record_df.rename(columns={"name": "사용자", "level": "층수"})
                display_df = display_df[["등수", "사용자", "층당 소요(초)", "층수", "날짜"]]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            with tabs[2]:
                st.subheader("최고 층수 (이력별)")
                best_df = df.copy()
                best_df["날짜"] = best_df["start_datetime"].str[:10]
                best_df = best_df.sort_values("level", ascending=False).reset_index(drop=True)
                best_df["등수"] = range(1, len(best_df) + 1)
                best_df["rank_display"] = best_df["등수"].apply(
                    lambda r: medal_map.get(r, str(r))
                )
                best_df["등수"] = best_df["rank_display"]
                display_cols = ["등수", "사용자", "최고 층수", "날짜"]
                display_df = best_df.rename(columns={"name": "사용자", "level": "최고 층수"})
                display_df = display_df[display_cols]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"리더보드 조회 중 오류가 발생했습니다: {e}")

elif menu == "이력 조회":
    st.header("계단 오르기 이력 조회")
    columns = st.columns([1, 1])
    with columns[0]:
        user_id_filter = st.text_input("사용자 ID로 검색 (공백 시 전체 조회)", key="user_id_input")
    with columns[1]:
        user_name_filter = st.text_input("사용자 이름으로 검색 (공백 시 전체 조회)", key="user_name_input")
    
    try:
        if user_id_filter:
            response = retrieve_history_by_user_id(int(user_id_filter))
        elif user_name_filter:
            response = retrieve_history_by_user_name(str(user_name_filter))
        else:
            response = retrieve_all_history_with_user_name()
            
        if response.status_code == StatusCode.SUCCESS.value:
            if response.history_list:
                # Sort by ID descending (latest first)
                history_list = sorted(response.history_list, key=lambda x: x.id, reverse=True)
                
                # Pagination settings
                items_per_page = 10
                total_items = len(history_list)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                
                if 'page' not in st.session_state:
                    st.session_state.page = 1
                
                # Bound page state
                if st.session_state.page > total_pages:
                    st.session_state.page = total_pages
                if st.session_state.page < 1:
                    st.session_state.page = 1

                start_idx = (st.session_state.page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                page_list = history_list[start_idx:end_idx]

                # CSV Download Button
                history_data = []
                for h in history_list:
                    history_data.append({
                        "ID": h.id,
                        "User ID": h.user_id,
                        "User Name": h.name,
                        "Start Time": h.start_datetime,
                        "End Time": h.end_datetime,
                        "Duration": h.duration,
                        "Level": h.level,
                        "Rest Count": h.rest_count,
                        "Heartbeat": h.heartbeat
                    })
                df_download = pd.DataFrame(history_data)
                csv = df_download.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="CSV 다운로드",
                    data=csv,
                    file_name=f"climbing_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.markdown("---")
                cols = st.columns([1, 1, 1, 2, 2, 1, 1, 1, 1, 1])
                cols[0].write("**ID**")
                cols[1].write("**사용자 ID**")
                cols[2].write("**사용자 이름**")
                cols[3].write("**시작 시간**")
                cols[4].write("**종료 시간**")
                cols[5].write("**소요(초)**")
                cols[6].write("**층수**")
                cols[7].write("**휴식**")
                cols[8].write("**심박수**")
                cols[9].write("**삭제**")
                st.markdown("---")

                for h in page_list:
                    with st.container():
                        cols = st.columns([1, 1, 1, 2, 2, 1, 1, 1, 1, 1])
                        cols[0].write(h.id)
                        cols[1].write(h.user_id)
                        cols[2].write(h.name)
                        cols[3].write(h.start_datetime)
                        cols[4].write(h.end_datetime)
                        cols[5].write(h.duration)
                        cols[6].write(h.level)
                        cols[7].write(f"{h.rest_count}회")
                        cols[8].write(h.heartbeat)
                        if cols[9].button("Delete", key=f"del_{h.id}"):
                            try:
                                body = DeleteStepHistoryRequestBody(id=h.id)
                                del_response = delete_step_history(body)
                                if del_response.status_code == StatusCode.SUCCESS.value:
                                    st.success(f"ID {h.id} 기록이 삭제되었습니다.")
                                    st.rerun()
                                else:
                                    st.error(f"삭제 실패: {del_response.message}")
                            except Exception as e:
                                st.error(f"오류 발생: {e}")

                st.markdown("---")
                page_cols = st.columns(total_pages + 2 if total_pages < 10 else 12)

                # Prev button
                if st.session_state.page > 1:
                    if page_cols[0].button("Prev", key="browse_prev"):
                        st.session_state.page -= 1
                        st.rerun()

                # Page numbers
                for i in range(total_pages):
                    if i < 10:
                        if page_cols[i+1].button(str(i+1), key=f"pg_{i+1}", type="primary" if st.session_state.page == i+1 else "secondary"):
                            st.session_state.page = i+1
                            st.rerun()

                # Next button
                if st.session_state.page < total_pages:
                    next_col_idx = min(total_pages + 1, 11)
                    if page_cols[next_col_idx].button("Next", key="browse_next"):
                        st.session_state.page += 1
                        st.rerun()
            else:
                st.info("조회된 기록이 없습니다.")
        else:
            st.error(f"오류 발생: {response.message}")
            
    except ValueError:
        st.error("올바른 사용자 ID(숫자)를 입력해주세요.")
    except Exception as e:
        st.error(f"예기치 못한 오류가 발생했습니다: {e}")

elif menu == "사용자 조회":
    st.header("👥 사용자 정보 조회")
    
    tab1, tab2 = st.tabs(["전체 조회", "이름 검색"])
    
    with tab1:
        try:
            response = retrieve_all_users()
            if response.status_code == StatusCode.SUCCESS.value:
                if response.user_list:
                    df_users = pd.DataFrame([u.dict() for u in response.user_list])
                    st.dataframe(df_users, use_container_width=True)
                else:
                    st.info("등록된 사용자가 없습니다.")
            else:
                st.error(f"오류 발생: {response.message}")
        except Exception as e:
            st.error(f"오류 발생: {e}")
                
    with tab2:
        search_name = st.text_input("조회할 사용자 이름 입력")
        if st.button("검색"):
            if search_name:
                try:
                    from schemas.users import RetrieveUserInfoByNameRequestBody
                    body = RetrieveUserInfoByNameRequestBody(name=search_name)
                    response = retrieve_user_info_by_name(body)
                    if response.status_code == StatusCode.SUCCESS.value:
                        if response.user_list:
                            df_search = pd.DataFrame([u.dict() for u in response.user_list])
                            st.dataframe(df_search, use_container_width=True)
                        else:
                            st.info("해당 이름의 사용자를 찾을 수 없습니다.")
                    else:
                        st.error(f"오류 발생: {response.message}")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
            else:
                st.warning("이름을 입력해주세요.")

elif menu == "기록 등록":
    st.header("📝 새 기록 등록")

    input_method = st.radio("등록 방식", ["단일 기록", "CSV 파일 일괄 등록"], horizontal=True)

    if input_method == "단일 기록":
        # 사용자 선택 방식 결정 (폼 외부로 이동하여 즉각적인 UI 변경 가능하게 함)
        user_selection_mode = st.radio("사용자 입력 방식", ["ID 직접 입력", "사용자 목록에서 선택"], horizontal=True)

        u_ids = []
        if user_selection_mode == "ID 직접 입력":
            user_ids_input = st.text_input("사용자 ID (쉼표로 구분)", placeholder="1, 2")
            if user_ids_input:
                try:
                    u_ids = [int(x.strip()) for x in user_ids_input.split(",") if x.strip()]
                except ValueError:
                    st.error("ID는 숫자여야 합니다.")
        else:
            try:
                user_resp = retrieve_all_users()
                if user_resp.status_code == StatusCode.SUCCESS.value and user_resp.user_list:
                    user_options = {f"{u.name} ({u.email})": u.id for u in user_resp.user_list}
                    selected_users = st.multiselect("사용자 선택", options=list(user_options.keys()))
                    u_ids = [user_options[name] for name in selected_users]
                else:
                    st.warning("사용자 목록을 불러올 수 없습니다.")
            except Exception as e:
                st.error(f"사용자 조회 중 오류 발생: {e}")

        with st.form("record_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_dt = st.text_input("시작 시간", placeholder="2026-05-12 09:00:00.000")
                level = st.number_input("오른 층수", min_value=0, step=1)
                rest_count = st.number_input("휴식 횟수", min_value=0, step=1)

            with col2:
                end_dt = st.text_input("종료 시간", placeholder="2026-05-12 09:10:00.000")
                heartbeat = st.number_input("평균 심박수", min_value=0.0, step=0.1)
                rest_level_str = st.text_input("휴식 층수 (쉼표로 구분)", placeholder="5, 10, 15")

            submit_button = st.form_submit_button("기록 저장")

            if submit_button:
                try:
                    r_levels = [int(x.strip()) for x in rest_level_str.split(",") if x.strip()] if rest_level_str else None

                    if not u_ids:
                        st.error("최소 한 명의 사용자 ID를 입력해주세요.")
                    elif not start_dt or not end_dt:
                        st.error("시작 시간과 종료 시간을 입력해주세요.")
                    else:
                        body = CreateStepHistoryRequestBody(
                            user_id=u_ids,
                            start_datetime=start_dt,
                            end_datetime=end_dt,
                            level=level,
                            rest_count=rest_count,
                            rest_level=r_levels,
                            heartbeat=heartbeat
                        )

                        response = create_step_history(body)
                        if response.status_code == StatusCode.SUCCESS.value:
                            st.success("기록이 성공적으로 저장되었습니다!")
                        else:
                            st.error(f"저장 실패: {response.message}")

                except ValueError as e:
                    st.error(f"입력 형식이 잘못되었습니다: {e}")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

    else:
        st.subheader("CSV 파일 업로드")
        st.markdown("""
        **CSV 형식** (1행은 헤더여야 합니다):

        | user_id | start_datetime | end_datetime | level | rest_count | rest_level | heartbeat |
        |---------|---------------|-------------|-------|------------|------------|-----------|
        | 1 | 2026-04-22 12:05:00 | 2026-04-22 12:12:00 | 19 | 1 | 12,15 | 167 |

        - `user_id`, `start_datetime`, `end_datetime`, `level`은 필수 항목입니다.
        - `rest_count`, `rest_level`, `heartbeat`는 선택 항목입니다.
        - `rest_level`은 쉼표로 여러 층수를 구분합니다 (예: 10,15).
        """)

        csv_file = st.file_uploader("CSV 파일을 선택해주세요", type=["csv"])

        if csv_file:
            try:
                csv_content = csv_file.read().decode("utf-8-sig")
                df_preview = pd.read_csv(pd.io.common.StringIO(csv_content))
                st.markdown("**미리보기**")
                st.dataframe(df_preview.head(10), use_container_width=True, hide_index=True)

                if st.button("CSV로 등록하기", type="primary"):
                    response = create_step_history_from_csv(csv_content)
                    st.session_state.csv_result = response

            except UnicodeDecodeError:
                st.error("파일 인코딩 오류가 발생했습니다. UTF-8로 저장된 CSV 파일을 업로드해주세요.")
            except Exception as e:
                st.error(f"파일 읽기 중 오류 발생: {e}")

        if "csv_result" in st.session_state:
            result = st.session_state.csv_result
            col1, col2, col3 = st.columns(3)
            col1.metric("성공", result.success_count)
            col2.metric("실패", result.fail_count)
            col3.metric("총 행 수", result.success_count + result.fail_count)

            if result.success_count > 0:
                st.success(result.message)
            if result.fail_count > 0:
                st.error(f"{result.fail_count}行的数据导入失败")
                for err in result.errors:
                    st.code(err)

            if st.button("결과 닫기"):
                st.session_state.pop("csv_result", None)
                st.rerun()

elif menu == "기록 수정":
    st.header("✏️ 기록 수정")

    if "edit_target_id" in st.session_state and st.session_state.edit_target_id is not None:
        target_id = st.session_state.edit_target_id
    else:
        target_id = None

    response = retrieve_all_history_with_user_name()

    if response.status_code != StatusCode.SUCCESS.value:
        st.error(f"오류 발생: {response.message}")
    else:
        all_history = sorted(response.history_list, key=lambda x: x.id, reverse=True)

        if target_id is not None:
            selected_record = None
            for h in all_history:
                if h.id == target_id:
                    selected_record = h
                    break

            if selected_record:
                st.session_state.edit_record = {
                    "id": selected_record.id,
                    "user_id": selected_record.user_id,
                    "name": selected_record.name,
                    "start_datetime": selected_record.start_datetime,
                    "end_datetime": selected_record.end_datetime,
                    "duration": selected_record.duration,
                    "level": selected_record.level,
                    "rest_count": selected_record.rest_count,
                    "rest_level": ", ".join(str(x) for x in selected_record.rest_level) if selected_record.rest_level else "",
                    "heartbeat": selected_record.heartbeat,
                }

                st.subheader(f"ID {selected_record.id} 기록 수정")
                info_col1, info_col2, info_col3 = st.columns(3)
                info_col1.metric("사용자 ID", selected_record.user_id)
                info_col2.metric("사용자 이름", selected_record.name)
                info_col3.metric("소요 시간(초)", selected_record.duration)
                st.markdown("---")

                col1, col2 = st.columns(2)
                with col1:
                    edit_start_dt = st.text_input(
                        "시작 시간",
                        value=st.session_state.edit_record["start_datetime"],
                        key="edit_start_dt",
                    )
                    edit_level = st.number_input(
                        "오른 층수",
                        value=st.session_state.edit_record["level"],
                        min_value=0,
                        step=1,
                        key="edit_level",
                    )
                    edit_rest_count = st.number_input(
                        "휴식 횟수",
                        value=st.session_state.edit_record["rest_count"] if st.session_state.edit_record["rest_count"] else 0,
                        min_value=0,
                        step=1,
                        key="edit_rest_count",
                    )

                with col2:
                    edit_end_dt = st.text_input(
                        "종료 시간",
                        value=st.session_state.edit_record["end_datetime"],
                        key="edit_end_dt",
                    )
                    edit_heartbeat = st.number_input(
                        "평균 심박수",
                        value=st.session_state.edit_record["heartbeat"] if st.session_state.edit_record["heartbeat"] else 0.0,
                        min_value=0.0,
                        step=0.1,
                        key="edit_heartbeat",
                    )
                    edit_rest_level_str = st.text_input(
                        "휴식 층수 (쉼표로 구분)",
                        value=st.session_state.edit_record["rest_level"],
                        placeholder="5, 10, 15",
                        key="edit_rest_level",
                    )

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    update_btn = st.button("수정", type="primary", use_container_width=True)
                with btn_col2:
                    cancel_btn = st.button("목록으로", use_container_width=True)

                if cancel_btn:
                    st.session_state.edit_target_id = None
                    st.session_state.pop("edit_record", None)
                    st.rerun()

                if update_btn:
                    try:
                        r_levels = None
                        if edit_rest_level_str:
                            r_levels = [int(x.strip()) for x in edit_rest_level_str.split(",") if x.strip()]

                        orig = st.session_state.edit_record
                        body = UpdateStepHistoryRequestBody(
                            id=target_id,
                            start_datetime=edit_start_dt if edit_start_dt != orig["start_datetime"] else None,
                            end_datetime=edit_end_dt if edit_end_dt != orig["end_datetime"] else None,
                            level=edit_level if edit_level != orig["level"] else None,
                            rest_count=edit_rest_count if edit_rest_count != (orig["rest_count"] or 0) else None,
                            rest_level=r_levels,
                            heartbeat=edit_heartbeat if edit_heartbeat != (orig["heartbeat"] or 0.0) else None,
                        )

                        update_resp = update_step_history(body)
                        if update_resp.status_code == StatusCode.SUCCESS.value:
                            st.success(f"ID {target_id} 기록이 수정되었습니다!")
                            st.session_state.pop("edit_record", None)
                            st.rerun()
                        else:
                            st.error(f"수정 실패: {update_resp.message}")
                    except ValueError as e:
                        st.error(f"입력 형식이 잘못되었습니다: {e}")
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
            else:
                st.error(f"ID {target_id}에 해당하는 기록을 찾을 수 없습니다.")
                if st.button("목록으로"):
                    st.session_state.edit_target_id = None
                    st.rerun()
        else:
            st.info("수정할 기록 ID를 아래에서 검색하여 선택해주세요.")
            search_id = st.text_input("기록 ID 검색", placeholder="예: 5", key="edit_search_id")

            if search_id:
                try:
                    search_id_int = int(search_id)
                    filtered = [h for h in all_history if h.id == search_id_int]
                except ValueError:
                    filtered = []
            else:
                filtered = all_history

            st.markdown("---")

            items_per_page = 10
            total_items = len(filtered)
            total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

            if 'edit_page' not in st.session_state:
                st.session_state.edit_page = 1
            if st.session_state.edit_page > total_pages:
                st.session_state.edit_page = total_pages
            if st.session_state.edit_page < 1:
                st.session_state.edit_page = 1

            start_idx = (st.session_state.edit_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_list = filtered[start_idx:end_idx]

            if not page_list:
                st.warning("해당 ID의 기록을 찾을 수 없습니다.")
            else:
                cols_header = st.columns([1, 1, 1, 2, 2, 1, 1, 1, 1, 1])
                cols_header[0].write("**ID**")
                cols_header[1].write("**사용자 ID**")
                cols_header[2].write("**사용자 이름**")
                cols_header[3].write("**시작 시간**")
                cols_header[4].write("**종료 시간**")
                cols_header[5].write("**소요(초)**")
                cols_header[6].write("**층수**")
                cols_header[7].write("**휴식**")
                cols_header[8].write("**심박수**")
                cols_header[9].write("**수정**")
                st.markdown("---")

                for h in page_list:
                    with st.container():
                        cols = st.columns([1, 1, 1, 2, 2, 1, 1, 1, 1, 1])
                        cols[0].write(h.id)
                        cols[1].write(h.user_id)
                        cols[2].write(h.name)
                        cols[3].write(h.start_datetime)
                        cols[4].write(h.end_datetime)
                        cols[5].write(h.duration)
                        cols[6].write(h.level)
                        cols[7].write(f"{h.rest_count}회")
                        cols[8].write(h.heartbeat)
                        if cols[9].button("수정", key=f"edit_{h.id}"):
                            st.session_state.edit_target_id = h.id
                            st.rerun()

            st.markdown("---")
            page_cols = st.columns(total_pages + 2 if total_pages < 10 else 12)

            if st.session_state.edit_page > 1:
                if page_cols[0].button("Prev", key="edit_prev"):
                    st.session_state.edit_page -= 1
                    st.rerun()

            for i in range(total_pages):
                if i < 10:
                    if page_cols[i+1].button(str(i+1), key=f"edit_pg_{i+1}", type="primary" if st.session_state.edit_page == i+1 else "secondary"):
                        st.session_state.edit_page = i+1
                        st.rerun()

            if st.session_state.edit_page < total_pages:
                next_col_idx = min(total_pages + 1, 11)
                if page_cols[next_col_idx].button("Next", key="edit_next"):
                    st.session_state.edit_page += 1
                    st.rerun()

elif menu == "이력 시각화":
    st.header("📊 계단 오르기 이력 시각화")
    
    try:
        response = retrieve_all_history_with_user_name()
        if response.status_code == StatusCode.SUCCESS.value and response.history_list:
            # 데이터프레임 변환
            data = []
            for h in response.history_list:
                
                try:
                    duration_per_level = h.duration/h.level
                except:
                    duration_per_level = 9999
                
                data.append({
                    "ID": h.id,
                    "사용자": h.name,
                    "시작": pd.to_datetime(h.start_datetime),
                    "소요시간": h.duration,
                    "층수": h.level,
                    "심박수": h.heartbeat,
                    "소요시간(1층당)": duration_per_level
                })
            df = pd.DataFrame(data).sort_values("시작")

            # 1. 시간 흐름에 따른 소요시간 변화
            st.subheader("⏱️ 사용자별 소요시간 변화")
            selected_user = st.selectbox("사용자 선택", options=df["사용자"].unique())
            user_df = df[df["사용자"] == selected_user].copy()
            
            if len(user_df) > 1:
                # 추세선 계산을 위해 x축을 숫자로 변환 (0, 1, 2...)
                x = np.arange(len(user_df))
                y = user_df["소요시간(1층당)"].values
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                user_df["추세선"] = p(x)
                
                st.line_chart(data=user_df, x="시작", y=["소요시간(1층당)", "추세선"])
                st.markdown(f"*({selected_user}님의 기록 순서대로 소요시간(초)과 추세선을 보여줍니다)*")
            elif len(user_df) == 1:
                st.line_chart(data=user_df, x="시작", y="소요시간(1층당)")
                st.info("데이터가 2개 이상이어야 추세선을 표시할 수 있습니다.")
            else:
                st.warning("데이터가 없습니다.")

            st.markdown("---")

            # 2. 사용자별 성과 비교 (총 층수 합계)
            st.subheader("🏆 사용자별 총 층수 성과 비교")
            user_performance = df.groupby("사용자")["층수"].sum().reset_index()
            st.bar_chart(data=user_performance, x="사용자", y="층수")

            st.markdown("---")

            # 3. 심박수 추이
            st.subheader("💓 심박수 변화 추이")
            st.line_chart(data=df, x="시작", y="심박수")

        else:
            st.info("시각화할 데이터가 없습니다.")
    except Exception as e:
        st.error(f"시각화 중 오류가 발생했습니다: {e}")
