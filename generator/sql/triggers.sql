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
      IF NEW.start_date > NEW.end_date THEN
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

CREATE OR REPLACE FUNCTION check_user_offer_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_offer_count INTEGER;
BEGIN
    -- number of offers with null status
    SELECT COUNT(*) INTO user_offer_count
    FROM offer
    WHERE LOGIN = NEW.LOGIN AND STATUS IS NULL;

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
    WHERE LOGIN = NEW.LOGIN AND DATE = NEW.DATE ;

    -- Check that user does not have multiple interviews at the same time
    IF user_interview_count >= 1 THEN
        RAISE EXCEPTION 'User can not have multiple interviews at the same time';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
