-- Functions
CREATE OR REPLACE FUNCTION check_salary()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.salary < 19242 THEN
    RAISE EXCEPTION 'Salary can not be less than (19242)';
  END IF;
  RETURN NEW;
END;

$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION check_dates()
RETURNS TRIGGER AS $$
BEGIN
      IF NEW.start_date >= NEW.end_date THEN
    RAISE EXCEPTION 'End date should be after start date';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_password_length()
RETURNS TRIGGER AS $$
BEGIN
  IF LENGTH(NEW.password) < 8 THEN
    RAISE EXCEPTION 'Minimum length of password is 8 symbols';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_user_devteam()
RETURNS TRIGGER AS $$
DECLARE
    user_teams_count INTEGER;
BEGIN
    -- number of devteam for current user
    SELECT COUNT(*) INTO user_teams_count
    FROM devrloper
    WHERE ЛОГИН = NEW.ЛОГИН;
    -- Check that user has no more than 1 team
    IF user_teams_count >= 1 THEN
        RAISE EXCEPTION 'User can not be a part of more than 1 team';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION check_user_offer_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_offer_count INTEGER;
BEGIN
    -- number of offers with null status
    SELECT COUNT(*) INTO user_offer_count
    FROM offer
    WHERE ЛОГИН = NEW.ЛОГИН AND СТАТУС IS NULL;

    -- Check that number of offers with null status is not more than 3
    IF user_offer_count > 3 THEN
        RAISE EXCEPTION 'User can not have more than 3 offers with null status';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_user_interview_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_interview_count INTEGER;
BEGIN
    -- number of interviews for user
    SELECT COUNT(*) INTO user_interview_count
    FROM techinterview
    WHERE ЛОГИН = NEW.ЛОГИН AND ДАТА = NEW.ДАТА;

    -- Check that user does not have multiple interviews at the same time
    IF user_interview_count >= 1 THEN
        RAISE EXCEPTION 'User can not have multiple interviews at the same time';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;





--Triggers
CREATE TRIGGER check_user_interview_limit_trigger
BEFORE INSERT ON techinterview
FOR EACH ROW
EXECUTE FUNCTION check_user_interview_limit();

CREATE TRIGGER check_user_offer_limit_trigger
BEFORE INSERT ON offer
FOR EACH ROW
EXECUTE FUNCTION check_user_offer_limit();

CREATE TRIGGER check_user_team_trigger
BEFORE INSERT ON developer
FOR EACH ROW
EXECUTE FUNCTION check_user_devteam();

CREATE TRIGGER check_password_length_trigger
BEFORE INSERT OR UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION check_password_length();

CREATE TRIGGER check_offer_salary_trigger
BEFORE INSERT OR UPDATE ON offer
FOR EACH ROW
EXECUTE FUNCTION check_salary();

CREATE TRIGGER check_contestdate_trigger
BEFORE INSERT OR UPDATE ON contest
FOR EACH ROW
EXECUTE FUNCTION check_dates();

CREATE TRIGGER check_offerdate_trigger
BEFORE INSERT OR UPDATE ON offer
FOR EACH ROW
EXECUTE FUNCTION check_dates();
