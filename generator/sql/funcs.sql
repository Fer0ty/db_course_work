CREATE OR REPLACE FUNCTION registration(
    p_login text,
    p_password text,
    p_email text,
    p_phone text,
    p_city text,
    p_name text,
    p_surname text,
    p_last_name text,
    p_birthdate date,
    p_role_name text
)
RETURNS VOID AS $$
DECLARE
    p_role_id INTEGER;
    my_account_id INTEGER;
BEGIN
    -- Вставка данных в таблицу "АККАУНТ"
    INSERT INTO accounts (password, email, phone_number, city)
    VALUES (p_password, p_email, p_phone, p_city)
    RETURNING account_id INTO my_account_id;

    -- Получение идентификатора роли
    SELECT id INTO p_role_id
    FROM roles
    WHERE name = p_role_name;

    -- Вставка данных в таблицу "ПОЛЬЗОВАТЕЛЬ"
    INSERT INTO users (login,account_id, name, surname, last_name, birthdate, role_id)
    VALUES (p_login, my_account_id, p_name, p_surname, p_last_name, p_birthdate, p_role_id);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION send_solution(
    p_login text,
    p_contest_id int,
    p_task_id int,
    p_user_answer text,
    p_solution_status boolean
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO problem_solution (login, contest_id, problem_id, user_answer, status)
    VALUES (p_login, p_contest_id, p_task_id, p_user_answer, p_solution_status);
END;
$$ LANGUAGE plpgsql;


--создание контеста
CREATE OR REPLACE FUNCTION plan_contest(
    p_name text,
    p_start_date date,
    p_end_date date,
    p_user_id int
)
RETURNS VOID AS $$
DECLARE
role_id INTEGER;
BEGIN
    SELECT roles.name INTO role_id FROM roles where roles.id =( SELECT role_id FROM users WHERE p_user_id = users.account_id);
    IF role_id <> 'COMPANY' THEN
    RAISE EXCEPTION 'Только пользователь с ролью "организатор" может запланировать контест';
    END IF;

    IF p_start_date >= p_end_date THEN
    RAISE EXCEPTION 'Дата начала должна быть меньше даты окончания';
    END IF;

    INSERT INTO contest(name, start_date, end_date, creator)
    VALUES (p_name, p_start_date, p_end_date, p_user_id);
END;
$$LANGUAGE plpgsql;

--создание тех.интервью

CREATE OR REPLACE FUNCTION plan_techinterview(
    p_user_login text,
    p_date timestamp,
    p_developer_login text
)
RETURNS VOID AS $$
    DECLARE
    role_id INTEGER;
    is_exist INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id =( SELECT role_id FROM users WHERE p_developer_login = users.account_id);
        IF role_id <> 'DEVELOPER' THEN
        RAISE EXCEPTION 'В качестве интервьюера можно назначить только пользователя с ролью "DEVELOPER"';
        END IF;

        SELECT COUNT(*) INTO is_exist FROM users where users.login = p_user_login;
        IF is_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в логине пользователя';
        END IF;
        INSERT INTO techinterview(login, date, interviwer_id)
        VALUES (p_user_login, p_date, p_developer_login);
END;
$$ LANGUAGE plpgsql;

--добавления фидбека по задаче
CREATE OR REPLACE FUNCTION add_feedback(
    p_hr_login text,
    p_techinterview_id int,
    p_comment text
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'HR' THEN
        RAISE EXCEPTION 'Только пользователь с ролью HR может оставить фидбек по задаче';
        END IF;
        UPDATE problem_feedback
        SET comment = p_comment
        WHERE techinterview_id = p_techinterview_id;
END;
$$LANGUAGE plpgsql;

--добавления задачи на интервью
CREATE OR REPLACE FUNCTION add_techproblem(
    p_hr_login text,
    p_techinterview_id int,
    p_problem_id int
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id =( SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'DEVELOPER' THEN
        RAISE EXCEPTION 'Только пользователь с ролью DEVELOPER может добавить задачку на техническое интервью';
        END IF;

        INSERT INTO problem_feedback(techinterview_id, problem_id)
        VALUES (p_techinterview_id, p_problem_id);
END;
$$LANGUAGE plpgsql;

--создание техинтервью
CREATE OR REPLACE FUNCTION plan_teaminterview(
    p_hr_login text,
    p_login text,
    p_techinterview int,
    p_date timestamp,
    p_developerteam_id int
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
        is_exist INTEGER;
        is_tech_exist INTEGER;
        is_devel_exist INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'HR' THEN
        RAISE EXCEPTION 'Только пользователь с ролью HR может оставить фидбек';
        END IF;

        SELECT COUNT(*) INTO is_exist FROM users where users.login = p_login;
        IF is_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в логине пользователя';
        END IF;

        SELECT COUNT(*) INTO is_tech_exist FROM techinterview where techinterview.techinterview_id = p_techinterview;
        IF is_tech_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id технического интервью';
        END IF;

        SELECT COUNT(*) INTO is_devel_exist FROM devteam where devteam.devteam_id = p_developerteam_id;
        IF is_devel_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id команды разработчиков';
        END IF;

        INSERT INTO teaminterview(login, techinterview_id, date, devteam_id)
        VALUES (p_login, p_techinterview, p_date, p_developerteam_id);
    end;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_techstatus(
    p_hr_login text,
    p_techint_id INT,
    p_status boolean
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
        is_tech_exist INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'HR' THEN
        RAISE EXCEPTION 'Только пользователь с ролью HR может оставить фидбек';
        END IF;

        SELECT COUNT(*) INTO is_tech_exist FROM techinterview where techinterview.techinterview_id = p_techint_id;
        IF is_tech_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id технического интервью';
        END IF;

        UPDATE techinterview
        SET status = p_status
        WHERE techinterview_id = p_techint_id;

    end;
$$LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_techintstatus(
    p_hr_login text,
    p_techint_id INT,
    p_status boolean
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
        is_tech_exist INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'HR' THEN
        RAISE EXCEPTION 'Только пользователь с ролью HR может добавить результат интервью';
        END IF;

        SELECT COUNT(*) INTO is_tech_exist FROM techinterview where techinterview.techinterview_id = p_techint_id;
        IF is_tech_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id технического интервью';
        END IF;

        UPDATE techinterview
        SET status = p_status
        WHERE techinterview_id = p_techint_id;

    end;
$$LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_teamintstatus(
    p_developer_login text,
    p_teamint_id INT,
    p_status boolean
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
        is_tech_exist INTEGER;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_developer_login = users.login);
        IF role_id <> 'DEVELOPER' THEN
        RAISE EXCEPTION 'Только пользователь с ролью DEVELOPER может добавить статус технического интервью';
        END IF;

        SELECT COUNT(*) INTO is_tech_exist FROM techinterview where techinterview.techinterview_id = p_teamint_id;
        IF is_tech_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id технического интервью';
        END IF;

        UPDATE teaminterview
        SET status = p_status
        WHERE techinterview_id = p_teamint_id;

    end;
$$LANGUAGE plpgsql;

--отправка оффера
CREATE OR REPLACE FUNCTION send_offer(
    p_hr_login text,
    p_user_login text,
    p_devteam_id int,
    p_salary int,
    p_start_date date,
    p_end_date date
)
RETURNS VOID AS $$
    DECLARE
        role_id INTEGER;
        is_user_exist INTEGER;
        is_devdeam_exist integer;
    BEGIN
        SELECT roles.name INTO role_id FROM roles where roles.id = (SELECT role_id FROM users WHERE p_hr_login = users.login);
        IF role_id <> 'HR' THEN
        RAISE EXCEPTION 'Только пользователь с ролью HR может отправить оффер';
        END IF;

        SELECT COUNT(*) INTO is_user_exist FROM users where users.login = p_user_login;
        IF is_user_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в логине пользователя';
        END IF;

        SELECT COUNT(*) INTO is_devdeam_exist FROM devteam where devteam.devteam_id = p_devteam_id;
        IF is_devdeam_exist <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id команды разработчиков';
        END IF;
        INSERT INTO offer(login, devteam_id, salary, start_date, end_date)
               VALUES (p_user_login, p_devteam_id, p_salary, p_start_date, p_end_date);

    end;
$$LANGUAGE plpgsql;

--отправка оффера
CREATE OR REPLACE FUNCTION reply_offer(
    p_user_login text,
    p_offer_id INT,
    p_status boolean
)
RETURNS VOID AS $$
    DECLARE
        is_offer_exists INTEGER;
        is_available INTEGER;
    BEGIN
        SELECT COUNT(*) INTO is_offer_exists FROM offer where offer.offer_id = p_offer_id;
        IF is_offer_exists <> 1 THEN
        RAISE EXCEPTION 'Ошибка в id оффера пользователя';
        END IF;

        SELECT count(*) INTO is_available FROM offer where offer.offer_id = p_offer_id and offer.login = p_user_login;
        IF is_available <> 2 THEN
            RAISE EXCEPTION 'Нельзя ответить на этот оффер';
        end if;

        UPDATE offer
        SET status = p_status
        WHERE offer_id = p_offer_id;


    end;
$$LANGUAGE plpgsql;