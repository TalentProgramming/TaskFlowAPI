# TaskFlow classroom API

Free-host ready Flask API for Chapter 8. Same paths and JSON as `TaskFlowApi`.

Demo login: `student@example.com` / `123456`

## Run locally

```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open http://127.0.0.1:8000/v1

From the Android emulator use `http://10.0.2.2:8000/v1/` as `API_BASE_URL`. A physical phone needs your PC’s LAN IP.

## Host for free on Render (HTTPS)

Render’s free web service sleeps after idle time. Wake it in a browser before a class demo, or the first Android call can hit the 15s OkHttp timeout.

1. Create a GitHub repo that contains this `api` folder (or push it as its own repo).
2. Sign up at [render.com](https://render.com) with GitHub. Free plan is enough.
3. **New → Web Service →** that repo.
4. If the repo is TaskFlow, set **Root Directory** to `api`.
5. Runtime **Python**. Build `pip install -r requirements.txt`. Start `gunicorn -b 0.0.0.0:$PORT main:app`.
6. Create the service. Copy the URL, for example `https://taskflow-api.onrender.com`.
7. Android `API_BASE_URL` must be `https://YOUR-SERVICE.onrender.com/v1/` (trailing slash).

Optional env var: `TOKEN_SECRET` (any long string). Tokens stay valid after the service restarts.

## Point Chapter 8 at it

On `dev/chapter8`:

1. Change the flavor `API_BASE_URL` in `app/build.gradle.kts` to your Render URL + `/v1/`.
2. Remove `.addInterceptor(ClassroomMockInterceptor())` from `NetworkModule`. If the mock stays, Retrofit never leaves the phone.
3. Sync Gradle and run `stagingDebug` or `prodDebug`.

## Routes

| Method | Path | Auth |
|---|---|---|
| POST | `/v1/auth/login` | no |
| GET | `/v1/profile/me` | Bearer |
| PUT | `/v1/profile/me` | Bearer |
| POST | `/v1/profile/me/photo` | Bearer + multipart `photo` |
| GET | `/v1/products?q=&page=` | no |
