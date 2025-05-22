import streamlit as st
import sqlite3

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# 로그인 / 회원가입 메뉴
if not st.session_state.logged_in:
    menu_option = st.sidebar.selectbox("MENU", ["로그인", "회원가입"])
else:
    menu_option = st.sidebar.selectbox("MENU", ["책 관리", "로그아웃"])

# 로그아웃
if menu_option == "로그아웃":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# 로그인
if menu_option == "로그인" and not st.session_state.logged_in:
    st.title("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    login_button = st.button("로그인")

    if login_button:
        conn = sqlite3.connect('book.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and password == user[2]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"{username}님, 환영합니다!")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# 회원가입
elif menu_option == "회원가입" and not st.session_state.logged_in:
    st.title("회원가입")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    passwordChk = st.text_input("비밀번호 확인")
    email = st.text_input("이메일")
    gender = st.text_input("성별")
    birthday = st.date_input("생일")
    age = st.number_input("나이", step=1)
    join_button = st.button("회원가입")

    if join_button:
        if password != passwordChk:
            st.warning("비밀번호가 일치하지 않습니다.")
        else:
            conn = sqlite3.connect('book.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                st.warning("이미 존재하는 아이디입니다.")
            else:
                c.execute('''
                    INSERT INTO users(username, password, email, gender, birthday, age)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password, email, gender, str(birthday), age))
                conn.commit()
                conn.close()
                st.success("회원가입 완료! 로그인 해주세요.")

# 책 관리 기능
if st.session_state.logged_in:
    menu_after_login = st.sidebar.selectbox("책 관리 메뉴", ["책 추가", "책 목록", "책 상태 관리"])

    # 책 추가
    if menu_after_login == "책 추가":
        st.title("책 추가")
        book_title = st.text_input("책 제목")
        book_author = st.text_input("책 저자")
        book_genre = st.text_input("책 장르")
        book_summary = st.text_area("책 요약")
        book_rating = st.slider("별점", 1, 5)
        add_book_btn = st.button("책 추가")

        if add_book_btn:
            conn = sqlite3.connect('book.db')
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ?", (st.session_state.username,))
            user_id = c.fetchone()[0]

            c.execute('''
                INSERT INTO books (title, author, genre, summary, rating, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book_title, book_author, book_genre, book_summary, book_rating, user_id))
            conn.commit()
            conn.close()
            st.success("책이 추가되었습니다!")

    # 책 목록
    elif menu_after_login == "책 목록":
        st.title("내 책 목록")
        conn = sqlite3.connect('book.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (st.session_state.username,))
        user_id = c.fetchone()[0]
        c.execute("SELECT * FROM books WHERE user_id = ?", (user_id,))
        books = c.fetchall()
        conn.close()

        if books:
            for book in books:
                st.write(f"📚 제목: {book[1]}, 저자: {book[2]}, 장르: {book[3]}, 별점: {book[5]}")
                st.write(f"📝 요약: {book[4]}")
                st.write("-" * 50)
        else:
            st.info("등록한 책이 없습니다.")

    # 책 상태 관리
    elif menu_after_login == "책 상태 관리":
        st.title("책 상태 관리")
        book_id = st.number_input("책 ID", min_value=1)
        status = st.selectbox("책 상태", ["읽음", "읽는 중", "읽을 예정"])
        read_date = st.date_input("읽은 날짜")
        if st.button("상태 저장"):
            conn = sqlite3.connect('book.db')
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username = ?", (st.session_state.username,))
            user_id = c.fetchone()[0]
            c.execute('''
                INSERT INTO logs (user_id, book_id, status, read_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, book_id, status, str(read_date)))
            conn.commit()
            conn.close()
            st.success("책 상태가 저장되었습니다.")
