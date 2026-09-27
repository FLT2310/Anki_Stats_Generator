from project import clean_anki_text, is_anki_package, calculate_retention_rate


def test_clean_anki_text():
    assert (
        clean_anki_text(
            "ja [sound:azure-05c38b4c-0813a860-2e845308-2bb68151-df077288.mp3]"
        )
        == "ja"
    )
    assert (
        clean_anki_text(
            "nee [sound: azure-c4a8bbb6-4bf81adc-5123daaf-0d6432cd-97bfa550.mp3]"
        )
        == "nee"
    )
    assert (
        clean_anki_text(
            "niet [sound: azure-4e7406c2-779b8efa-8c40763d-b2dd07ad-e9caf9e9.mp3]"
        )
        == "niet"
    )
    assert (
        clean_anki_text(
            "roken [sound:azure-c5b3c1fb-80894807-30a30196-8b827196-3469e0a8.mp3]"
        )
        == "roken"
    )
    assert (
        clean_anki_text(
            "wel [sound:azure-082deaff-51595584-94ec7599-a4cef2a3-843e4f11.mp3]"
        )
        == "wel"
    )


def test_is_anki_package():
    assert is_anki_package("LearnDutch.org-1000.apkg") == True
    assert is_anki_package("LearnDutch.org-1000.zip") == False
    assert is_anki_package("LearnDutch.org-1000.zip.apkg") == True
    assert is_anki_package(2) == False
    assert is_anki_package("LearnDutch.org-1000.zip.APKG") == True


def test_calculate_retention_rate():
    assert calculate_retention_rate(1253, 2420) == 34.11
    assert calculate_retention_rate(0, 0) == 0.00
    assert calculate_retention_rate(0, 2420) == 0.00
    assert calculate_retention_rate(12, 9) == 57.14
    assert calculate_retention_rate(200000, 1) == 100.00
