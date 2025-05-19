import pytest
from playwright.sync_api import sync_playwright, APIRequestContext
import json

BASE_URL = "http://testovani.kitner.cz/"
APP_PATH = "regkurz/formsave.php"
URL_APP = f"{BASE_URL}{APP_PATH}"


@pytest.fixture(scope="session")
def api_context() -> APIRequestContext:
    playwright = sync_playwright().start()
    context = playwright.request.new_context()
    yield context
    playwright.stop()


def send_registration(
    api_context,
    targetid, kurz, name, surname, email, phone,
    person, address, ico, count, comment, souhlas, expected_status
):
    payload = {
        "targetid": targetid,
        "kurz": kurz,
        "name": name,
        "surname": surname,
        "email": email,
        "phone": phone,
        "person": person,
        "count": count,
        "comment": comment,
        "souhlas": souhlas
    }

    if person == "fyz":
        payload["address"] = address
    elif person == "pra":
        payload["ico"] = ico

    response = api_context.post(URL_APP, data=payload)
    actual_status = response.status
    response_text = response.text()

    # 🚨 ALERT for unexpected formats that should return error but don't
    if expected_status == "500" and actual_status == 200:
        print("⚠️ ALERT: Expected failure (500), but received 200 OK")
        print(f"Test input (payload): {payload}")
        print(f"Response body:\n{response_text}")

    # 🚨 ALERT for unexpected 500 error
    if expected_status == "200" and actual_status == 500:
        print("❌ ALERT: Expected success (200), but received 500")
        print(f"Test input (payload): {payload}")
        print(f"Response body:\n{response_text}")

    # Main assertion
    assert actual_status == int(expected_status), (
        f"\n❌ Status code mismatch:\n"
        f"Expected: {expected_status}\n"
        f"Actual: {actual_status}\n"
        f"Payload:\n{json.dumps(payload, indent=2)}\n"
        f"Response:\n{response_text}"
    )

    if expected_status == "200":
        try:
            body = json.loads(response_text)
        except json.JSONDecodeError:
            pytest.fail(
                f"\n❌ Expected valid JSON in 200 response, but got invalid JSON.\n"
                f"Response body:\n{response_text}"
            )

        assert body["response"] == expected_status
        assert body["kurz"] == kurz
        assert body["name"] == name
        assert body["surname"] == surname
        assert body["email"] == email
        assert body["phone"] == phone
        assert body["person"] == person
        assert body["count"] == count
        assert body["comment"] == comment
        assert body["souhlas"] == souhlas

        if person == "fyz":
            assert body["address"] == address
            assert body.get("ico") in [None, ""]
        elif person == "pra":
            assert body["ico"] == ico
            assert body.get("address") in [None, ""]

    return response

# --- TEST CASES ---
# ✅ POZITIVNI TESTY✅
def test_registrace_fyz_person(api_context):
    response=send_registration(api_context,"1", "2", "Jan", "Novák","jan.novak@abc.cz","608123123", "fyz","Brno","27232433", "1", "ahoj", "True", 200)

def test_registrace_pra_person(api_context):
    response=send_registration(api_context,"1", "2", "Jan", "Novák","jan.novak@abc.cz","608123123", "pra","Brno","27232433", "1", "ahoj", "True", 200)

def test_registrace_dlouhy_comment(api_context):
    response=send_registration(api_context,"1", "2", "Jan", "Novák","jan.novak@abc.cz","608123123", "fyz","Brno","27232433", "1", 1000000*"ahoj", "True", 200)

def test_registrace_fyz_person_minimal_input(api_context):
    send_registration(api_context, "1", "2", "A", "B", "a@b.cz", "111222333", "fyz", "Praha", "00000000", "1", "", "True", 200)

def test_registrace_fyz_person_long_name(api_context):
    send_registration(api_context, "1", "2", "Jan"*20, "Novák"*20, "long.name@example.com", "777888999", "fyz", "Brno", "27232433", "1", "Test dlouhého jména", "True", 200)

def test_registrace_valid_different_kurz(api_context):
    send_registration(api_context, "1", "3", "Lucie", "Krásná", "lucie@example.cz", "777123456", "fyz", "Olomouc", "11112222", "3", "Zájem o kurz číslo 5", "True", 200)

def test_registrace_valid_international_format_plus420(api_context):
    send_registration(api_context, "1", "2", "Eva", "Mezinárodní", "eva@example.cz", "+420777123456", "fyz", "Brno", "27232433", "1", "Valid +420 phone", "True", 200)

def test_registrace_name_with_diacritics(api_context):
    send_registration(api_context, "1", "2", "Šárka", "Černá", "sarka@example.cz", "777123456", "fyz", "Brno", "27232433", "1", "Diacritics test", "True", 200)

def test_registrace_name_with_hyphen(api_context):
    send_registration(api_context, "1", "2", "Anna-Marie", "Nováková", "anna@example.cz", "777123456", "fyz", "Praha", "12345678", "1", "Hyphen name", "True", 200)

def test_registrace_name_with_accents(api_context):
    send_registration(api_context, "1", "2", "José", "García", "jose@example.cz", "777123456", "fyz", "Brno", "27232433", "1", "Accents in name", "True", 200)

def test_registrace_name_with_german_umlauts(api_context):
    send_registration(api_context, "1", "2", "Müller", "Schröder", "muller@example.cz", "777123456", "fyz", "Ostrava", "87654321", "1", "German umlauts", "True", 200)

def test_registrace_name_with_french_characters(api_context):
    send_registration(api_context, "1", "2", "Émilie", "Dùpont", "emilie@example.cz", "777123456", "fyz", "Plzeň", "12345678", "1", "French characters", "True", 200)

def test_registrace_name_with_nordic_letters(api_context):
    send_registration(api_context, "1", "2", "Åsa", "Jönsson", "asa@example.cz", "777123456", "fyz", "Brno", "87654321", "1", "Nordic characters", "True", 200)

def test_registrace_name_with_cyrillic(api_context):
    send_registration(api_context, "1", "2", "Алексей", "Иванов", "aleksey@example.cz", "777123456", "fyz", "Brno", "87654321", "1", "Cyrillic name", "True", 200)

def test_registrace_name_with_greek(api_context):
    send_registration(api_context, "1", "2", "Αλέξανδρος", "Παπαδόπουλος", "alex@example.cz", "777123456", "fyz", "Brno", "87654321", "1", "Greek name", "True", 200)

def test_registrace_name_with_japanese(api_context):
    send_registration(api_context, "1", "2", "太郎", "山田", "taro@example.cz", "777123456", "fyz", "Brno", "87654321", "1", "Japanese characters", "True", 200)

def test_registrace_name_with_digits(api_context):
    send_registration(api_context, "1", "2", "J4n", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Digits in name", "True", 200)

def test_registrace_name_with_symbols(api_context):
    send_registration(api_context, "1", "2", "J@n!", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Symbols in name", "True", 200)

def test_registrace_surname_with_digits(api_context):
    send_registration(api_context, "1", "2", "Jan", "Nov4k", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Digits in surname", "True", 200)

def test_registrace_surname_with_symbols(api_context):
    send_registration(api_context, "1", "2", "Jan", "N0v@k!", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Symbols in surname", "True", 200)

def test_registrace_surname_too_long(api_context):
    long_surname = "Novák" * 100  # Adjust based on backend limits
    send_registration(api_context, "1", "2", "Jan", long_surname, "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Too long surname", "True", 200)

def test_registrace_surname_encoded_script(api_context):
    send_registration(api_context, "1", "2", "Jan", '%3Cscript%3Ealert%28%22XSS%22%29%3C%2Fscript%3E', "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Encoded script in surname", "True", 200)

def test_registrace_surname_only_spaces(api_context):
    send_registration(api_context, "1", "2", "Jan", "     ", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Spaces only in surname", "True", 200)

def test_registrace_valid_count_1(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "valid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Count is 1", "True", 200)

def test_registrace_valid_count_5(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "valid@example.cz", "777123456", "fyz", "Brno", "12345678", "5", "Count is 5", "True", 200)

def test_registrace_valid_count_large(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "valid@example.cz", "777123456", "fyz", "Brno", "12345678", "999", "Count is 999", "True", 200)

def test_registrace_count_negative(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "-1", "Negative count", "True", 200)
#❌NEGATIVNI TESTY❌
#NAME FORMAT
def test_registrace_name_with_script(api_context):
    send_registration(api_context, "1", "2", "<script>alert('XSS')</script>", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Script in name", "True", 500)

def test_registrace_invalid_name_empty(api_context):
    send_registration(api_context, "1", "2", "", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Empty name", "True", 500)

#SURNAME FORMAT
def test_registrace_surname_with_script(api_context):
    send_registration(api_context, "1", "2", "Jan", "<script>alert('XSS')</script>", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Script in surname", "True", 500)

def test_registrace_invalid_surname_empty(api_context):
    send_registration(api_context, "1", "2", "Jan", "", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "1", "Empty surname", "True", 500)
#ICO FORMAT
def test_registrace_spatny_ico_format(api_context):
    response=send_registration(api_context,"1", "2", "Jan", "Novák","jan.novak@abc.cz","608123123", "pra","Brno","2723243", "1", "ahoj", "True", 500)

def test_registrace_spatny_ico_format_too_short(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "1234567", "1", "ahoj", "True", 500)

# Too long (9 digits)
def test_registrace_spatny_ico_format_too_long(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "123456789", "1", "ahoj", "True", 500)

# Contains letters
def test_registrace_spatny_ico_format_letters(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "12A45678", "1", "ahoj", "True", 500)

# Special characters
def test_registrace_spatny_ico_format_special_chars(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "12-45678", "1", "ahoj", "True", 500)

# All zeroes (syntactically valid, but might be invalid depending on backend logic)
def test_registrace_spatny_ico_format_all_zeroes(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "00000000", "1", "ahoj", "True", 500)

# Empty IČO
def test_registrace_spatny_ico_format_empty(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "608123123", "pra", "Brno", "", "1", "ahoj", "True", 500)


#EMAIl FORMAT
def test_registrace_email_x_at_dot_cz(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x@.cz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_at_e_dot_cz(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "@e.cz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_x_at_e_dot(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x@e.", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_x_at_xcz(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x@xcz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_with_spaces_around_at(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x    @x.cz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_with_space_before_dot(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x@x .cz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_with_multiple_spaces(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "x@x     .cz", "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_with_unicode_(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", '🦄@e.cz', "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_with_script(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", '<script>alert("Hello!");</script>@example.com', "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_email_encoded_script(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", 'text=%3Cscript%3Ealert%28%22Hello%21%22%29%3B%3C%2Fscript%3E%40example.com', "608123123", "pra", "Brno", "27232433", "1", "ahoj", "True", 500)

def test_registrace_empty_email(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "", "608123123", "fyz", "Brno", "27232433", "1", "Empty email", "True", 500)

#PHONE FORMAT

# Too long (12 digits)
def test_registrace_invalid_phone_too_long(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "420777123456", "fyz", "Brno", "27232433", "1", "Too long phone", "True", 500)

# Starts with zero (still might be OK, but assuming invalid here)
def test_registrace_invalid_phone_starts_with_zero(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "0777123456", "fyz", "Brno", "27232433", "1", "Starts with 0", "True", 500)

# Too short (8 digits)
def test_registrace_invalid_phone_too_short(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "77712345", "fyz", "Brno", "27232433", "1", "Too short phone", "True", 500)

# Too long (10 digits)
def test_registrace_invalid_phone_too_long_10_digits(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "7771234567", "fyz", "Brno", "27232433", "1", "10-digit phone", "True", 500)

# Contains letter
def test_registrace_invalid_phone_contains_letter(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "777a23456", "fyz", "Brno", "27232433", "1", "Contains letter", "True", 500)

# Contains special character
def test_registrace_invalid_phone_special_char(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "777123@56", "fyz", "Brno", "27232433", "1", "Special char in phone", "True", 500)

# Empty phone number
def test_registrace_empty_phone_number(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "jan.novak@abc.cz", "", "fyz", "Brno", "27232433", "1", "Empty phone", "True", 500)

#COUNT FORMAT
# Zero count
def test_registrace_invalid_count_zero(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "0", "Zero count", "True", 500)

# Negative count
def test_registrace_count_negative(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "-1", "Negative count", "True", 500)

# Decimal number
def test_registrace_invalid_count_decimal(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "2.5", "Decimal count", "True", 500)

# Non-numeric string
def test_registrace_invalid_count_text(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "two", "Text in count", "True", 500)

# Empty string
def test_registrace_invalid_count_empty(api_context):
    send_registration(api_context, "1", "2", "Jan", "Novák", "invalid@example.cz", "777123456", "fyz", "Brno", "12345678", "", "Empty count", "True", 500)