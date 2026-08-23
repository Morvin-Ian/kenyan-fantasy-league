# Users are forcefully logged out when the backend is temporarily unavailable (e.g., during `docker compose down` / `docker compose up`)

## What happened

When a user runs `docker compose down` followed by `docker compose up` on the Kenyan Fantasy League project, all currently logged-in users are ejected from their sessions, even though their JWT tokens had not expired. The tokens are deleted from `localStorage` in the browser, forcing every user to sign in again.

## Root cause

Two parts of the code conspire to destroy valid tokens on transient errors:

1. **`refreshUserProfile()` called `logout()` on *any* error, not just auth failures.**
   In `client/src/stores/auth.ts`, the catch block of `refreshUserProfile()` (pre-fix) unconditionally called `this.logout()`:

   ```typescript
   catch (error: any) {
       await this.logout();
       throw error;
   }
   ```

   This means a transient network error (e.g., connection refused while the API container is restarting), a 5xx, or any non-401 error permanently deletes the user's tokens from `localStorage`.

2. **The Axios interceptor already handles 401 / token-refresh correctly.**
   In `client/src/axios-interceptor.ts` (lines 47–98), the response interceptor already:
   - Catches 401 responses;
   - Attempts a silent token refresh via `authStore.refreshToken()` (line 74);
   - Retries the original request if refresh succeeds (line 78);
   - Calls `authStore.logout()` and redirects to `/sign-in` only if refresh fails (lines 63–65, 82–84).

   Since the interceptor runs *before* the calling code's catch block, the `logout()` in `refreshUserProfile()` was redundant for 401 errors — but destructive for all *other* error types.

**Sequence of events during `docker compose down && docker compose up`:**

1. User is logged in with valid tokens in `localStorage`.
2. `docker compose down` stops all containers, including the API and client.
3. `docker compose up` starts new containers. The client app loads in the browser.
4. `authStore.initialize()` is called (from `App.vue` or a view's `onMounted`). It reads the token back from `localStorage` (`client/src/stores/auth.ts:235-242`) and calls `refreshUserProfile()`, which issues `GET /api/v1/profile` (`client/src/stores/auth.ts:203`).
5. If the API container isn't ready yet, the request fails with a **network error** (not 401).
6. The interceptor doesn't handle non-401 errors, so they fall through to `refreshUserProfile()`'s catch block (`client/src/axios-interceptor.ts:97`).
7. The catch block (pre-fix) called `this.logout()` (`client/src/stores/auth.ts:162-166`), which calls `setToken(null, null)` (`client/src/stores/auth.ts:47-61`), which runs `localStorage.removeItem("token")` and `localStorage.removeItem("refresh")`.
8. **The tokens are gone.** The user is permanently logged out even though the tokens were perfectly valid. The logout only stops being destructive if the user happened to have `authStore.user` already set, because `refreshUserProfile()` early-returns at lines 198–200 — which is why the bug is intermittent and appears "random" depending on navigation timing.

## Suggested fix

**Remove the `await this.logout()` call from `refreshUserProfile()`'s catch block.** The axios interceptor already handles 401 errors (including failed token refresh) by logging the user out. For all other transient errors (network, 5xx, etc.), the user should *not* lose their session — they should just see a transient error message.

Change in `client/src/stores/auth.ts`, method `refreshUserProfile()`:

```typescript
// Before (buggy):
catch (error: any) {
    await this.logout();
    throw error;
}

// After (fixed):
catch (error: any) {
    throw error;
}
```

The error still propagates to the caller (e.g., `HomeView.vue` or `TeamView.vue`), which can display an appropriate error message. But the user's tokens survive, so a subsequent page load or retry will succeed once the backend is available again.

## Applied fix

Edited `client/src/stores/auth.ts` — removed the `await this.logout();` call from the `catch` block in `refreshUserProfile()`. The method now simply re-throws the error (verified in the current code, lines 210–211):

```typescript
} catch (error: any) {
    throw error;
} finally {
    this.setLoading(false);
}
```

without destroying the stored tokens, relying on the axios response interceptor in `client/src/axios-interceptor.ts` to handle true authentication failures (401 + failed refresh) by logging the user out only when appropriate.

## How to verify

1. Log in to the app so valid tokens are stored in `localStorage`.
2. Run `docker compose down && docker compose up`.
3. Reload the page immediately (before the API container is healthy).
4. Before the fix: `localStorage` no longer contains `token`/`refresh` and the user lands on `/sign-in`.
5. After the fix: `localStorage` still contains `token`/`refresh`; a short error/loading state may show, and once the API answers, the profile loads and the user stays signed in.

---

## Error details

```
Now i have an issue on the kenyan fantasy repo, when i docker compose down, all the logged in user profiles initially are logged out even if the tokens had not expired. How do i report this incident on the kenyan fantasy league repo to create a pr, give me the process, it has somehting with the axios where if an error occurs, the tokens are deleted i guess, look into that
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `manual`
- First seen: 2026-07-23T20:20:57+00:00
- Fingerprint: `cdc28cfb67e2100a`

---

## Error details

```
2026-08-23 08:15:40 [ERROR] django.security.DisallowedHost.response_for_exception:124 - Invalid HTTP_HOST header: 'site.fantasykenya.com'. You may need to add 'site.fantasykenya.com' to ALLOWED_HOSTS.
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.10/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
  File "/usr/local/lib/python3.10/site-packages/django/middleware/common.py", line 48, in process_request
    host = request.get_host()
  File "/usr/local/lib/python3.10/site-packages/django/http/request.py", line 150, in get_host
    raise DisallowedHost(msg)
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'site.fantasykenya.com'. You may need to add 'site.fantasykenya.com' to ALLOWED_HOSTS.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `logfile:/root/kenyan-fantasy-league/logs/fantasy_league.log`
- First seen: 2026-08-23T05:16:09+00:00
- Fingerprint: `e75bee8fa703da7b`
