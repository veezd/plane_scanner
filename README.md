# plane_scanner
Repozytorium projektu zaliczeniowego przedmiotu "Wprowadzenie do baz danych". Aplikacja korzystając z OpenSky API zwraca informacje o ruchu lotniczym.

## Uruchomienie aplikacji
Aby włączyć program, wystarczy uruchomić plik `run.py`. Skrypt ten jest w pełni zautomatyzowany - samodzielnie utworzy wirtualne środowisko (`.venv`), a następnie zainstaluje wszystkie wymagane biblioteki przy użyciu menedżera pakietów `pip`.

```bash
python run.py
=======
# Plane Scanner

Projekt zaliczeniowy z przedmiotu **„Wprowadzenie do baz danych”**. Aplikacja monitoruje i zwraca informacje o bieżącym ruchu lotniczym nad Polską, wykorzystując w czasie rzeczywistym dane udostępniane przez [OpenSky Network API](https://opensky-network.org/).

---

## Wymagania wstępne i konfiguracja

Aby aplikacja mogła pobierać dane, wymagane jest posiadanie aktywnego konta w serwisie OpenSky oraz lokalne skonfigurowanie poświadczeń.

1. Zarejestruj darmowe konto na stronie [OpenSky Network](https://opensky-network.org/).
2. W zakładce /my-opensky/account wygeneruj klucz API, pobierz plik credentials.json i upewnij się, że ma poniższą strukturę:

```json
{"clientId":"clientID-example","clientSecret":"clientSecret-example"}

```

3. Umieść ten plik w głównym katalogu projektu.

## Uruchomienie aplikacji

Proces uruchamiania został w pełni zautomatyzowany za pomocą skryptu startowego `run.py`. Skrypt ten automatycznie:

* Tworzy nowe wirtualne środowisko w folderze `.venv`.
* Instaluje wszystkie wymagane biblioteki zdefiniowane w projekcie przy użyciu menedżera pakietów `pip`.

Aby uruchomić aplikację, otwórz terminal w głównym katalogu projektu i wykonaj poniższe polecenie:

```bash
python run.py

```
