-- SQLite
-- select * from member_test 
-- where date(reg_date)="2025-09-17";

----------------------------------------
-- 날짜만 변경하는 쿼리 (|| : 문자열 연결)
----------------------------------------
-- update member_test 
-- set reg_date = "2025-09-19" || substr(reg_date, 11)
-- where id = 2;

-- delete FROM member where employee_id = "101008";

-- INSERT INTO member (employee_id, name)
-- VALUES 
--     ("101008", "차요준");


----------------------------------------
-- 출근 기록만 있는 사원 (101002)
----------------------------------------
INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101002, '2025-09-22', '2025-09-22 08:55:00', NULL,
    'FC', NULL,
    'in_101002.jpg', NULL,
    '2025-09-22 08:55:00', ''
);

----------------------------------------
-- 퇴근 기록만 있는 사원 (101002)
----------------------------------------
INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101002, '2025-09-22', NULL, '2025-09-22 18:00:00',
    NULL, 'FC',
    NULL, 'out_1001_1.jpg',
    '2025-09-22 18:00:00', ''
);

INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101002, '2025-09-22', NULL, '2025-09-22 18:05:00',
    NULL, 'ID',
    NULL, 'out_1001_2.jpg',
    '2025-09-22 18:05:00', '중복 퇴근'
);


----------------------------------------
-- 정상 출퇴근 (101007)
----------------------------------------
-- 출근
INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101007, '2025-09-22', '2025-09-22 09:02:00', NULL,
    'ID', NULL,
    'in_1002.jpg', NULL,
    '2025-09-22 09:02:00', ''
);

-- 퇴근
INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101007, '2025-09-22', NULL, '2025-09-22 18:20:00',
    NULL, 'FC',
    NULL, 'out_1002.jpg',
    '2025-09-22 18:20:00', ''
);



----------------------------------------
-- 출근만 있고 퇴근 없음 (101003)
----------------------------------------
INSERT INTO attendance (
    employee_id, check_date, check_in, check_out,
    check_in_method, check_out_method,
    check_in_img, check_out_img,
    reg_date, memo
)
VALUES (
    101003, '2025-09-22', '2025-09-22 08:40:00', NULL,
    'FC', NULL,
    'in_1003.jpg', NULL,
    '2025-09-22 08:40:00', '퇴근 누락?'
);
