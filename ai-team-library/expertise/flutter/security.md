# Flutter Security Conventions

## Core Principles

1. **Never trust the client.** All security enforcement happens server-side.
   Client-side checks are UX, not security.
2. **No secrets in the app bundle.** APKs and IPAs can be decompiled. API keys,
   signing secrets, and credentials never go in source or assets.
3. **Encrypt sensitive data at rest.** Local storage is accessible on rooted/
   jailbroken devices.

---

## Secrets Management

### Rules

- **Never hardcode** API keys, tokens, signing keys, or credentials in Dart
  source, assets, or `pubspec.yaml`.
- Use `--dart-define` or `--dart-define-from-file` for build-time configuration
  that varies by environment. These values are compiled into the binary but are
  not as easily extractable as plain strings.
- For truly sensitive keys (payment processors, internal APIs), proxy through
  your backend. The mobile app authenticates to your backend; your backend calls
  the third-party API with the real key.
- Use `flutter_secure_storage` for storing tokens and credentials at runtime. It
  uses Keychain (iOS) and EncryptedSharedPreferences (Android).

```dart
// Build-time config (non-secret, environment-specific)
const apiBaseUrl = String.fromEnvironment('API_BASE_URL');

// Runtime secure storage (tokens, credentials)
final secureStorage = FlutterSecureStorage();
await secureStorage.write(key: 'auth_token', value: token);
final token = await secureStorage.read(key: 'auth_token');
```

---

## Authentication and Session Management

### Rules

- Store auth tokens in `flutter_secure_storage`, never in `shared_preferences`
  or plain files.
- Implement token refresh transparently via `dio` interceptors. The UI layer
  should never handle token expiry directly.
- Clear all stored credentials on logout. Call `secureStorage.deleteAll()`.
- Implement session timeout. Invalidate tokens after a configurable idle period.
- Use biometric authentication (`local_auth` package) as a second factor, not
  as the sole authentication mechanism.

```dart
// Dio interceptor for automatic token refresh
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this.secureStorage, required this.authApi});

  final FlutterSecureStorage secureStorage;
  final AuthApi authApi;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await secureStorage.read(key: 'auth_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Retry the original request with new token
        handler.resolve(await _retry(err.requestOptions));
        return;
      }
    }
    handler.next(err);
  }
}
```

---

## Network Security

### Rules

- Use HTTPS for all API communication. No exceptions.
- Implement certificate pinning for high-security apps using `dio` or
  `http_certificate_pinning`. Pin the leaf certificate or public key, not the
  root CA.
- Validate all server responses. Do not trust response structure — parse with
  `freezed`/`json_serializable` which enforce expected types.
- Set timeouts on all HTTP requests. Unbounded requests can hang the app.
- Do not log full request/response bodies in production. Redact tokens, passwords,
  and PII from logs.

```dart
// Dio with security configuration
final dio = Dio(BaseOptions(
  baseUrl: apiBaseUrl,
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
  headers: {'Content-Type': 'application/json'},
));
```

---

## Local Data Security

### Rules

- Use `flutter_secure_storage` for credentials and tokens.
- Use `drift` with SQLCipher for encrypted local databases when storing sensitive
  user data.
- Do not cache sensitive data (financial info, health records, PII) in plain
  `shared_preferences`.
- Clear sensitive cached data when the user logs out.
- Implement app lock (PIN/biometric) for apps handling sensitive data.
- Disable screenshots on sensitive screens using
  `SystemChrome.setEnabledSystemUIMode` or platform-specific flags.

---

## Input Validation

### Rules

- Validate all user input on the client for UX (immediate feedback) **and** on
  the server for security (authoritative validation).
- Sanitize text input before display to prevent XSS in `WebView` contexts.
- Use parameterized queries in `drift`/SQLite. Never concatenate user input into
  SQL strings.
- Validate deep link parameters before navigation. Malicious deep links can pass
  arbitrary data.
- Validate file uploads: check MIME type, file size, and file extension before
  processing.

---

## Platform-Specific Security

### Android

- Set `android:allowBackup="false"` in `AndroidManifest.xml` to prevent backup
  of app data.
- Set `android:networkSecurityConfig` to enforce HTTPS and certificate pinning.
- Enable ProGuard/R8 for release builds to obfuscate code.
- Use `EncryptedSharedPreferences` (via `flutter_secure_storage`) instead of
  plain `SharedPreferences`.

### iOS

- Enable App Transport Security (ATS). Do not add blanket `NSAllowsArbitraryLoads`
  exceptions.
- Use Keychain (via `flutter_secure_storage`) for credential storage.
- Enable data protection entitlement for sensitive files.
- Set `ITSAppUsesNonExemptEncryption` correctly for App Store compliance.

---

## Dependency Security

### Rules

- Audit dependencies before adding them. Check pub.dev scores, maintenance
  status, and open issues.
- Pin dependency versions in `pubspec.yaml`. Use exact versions, not ranges,
  for production dependencies.
- Run `flutter pub outdated` regularly to identify packages with known
  vulnerabilities.
- Prefer well-maintained packages with verified publishers on pub.dev.
- Review native dependencies (CocoaPods, Gradle) for known CVEs.
- Minimize the number of dependencies. Each dependency is an attack surface.

---

## Security Checklist

- [ ] No API keys, tokens, or secrets in source code or assets
- [ ] Auth tokens stored in `flutter_secure_storage`, not `shared_preferences`
- [ ] Token refresh handled transparently via interceptor
- [ ] All credentials cleared on logout
- [ ] HTTPS enforced for all API communication
- [ ] Certificate pinning implemented (if high-security requirement)
- [ ] All user input validated client-side and server-side
- [ ] Deep link parameters validated before navigation
- [ ] `android:allowBackup="false"` set in AndroidManifest
- [ ] ProGuard/R8 enabled for Android release builds
- [ ] App Transport Security enabled on iOS (no blanket exceptions)
- [ ] Sensitive data encrypted at rest
- [ ] Dependencies audited and pinned
- [ ] No PII or secrets in log output
- [ ] Release builds use `--obfuscate --split-debug-info`
