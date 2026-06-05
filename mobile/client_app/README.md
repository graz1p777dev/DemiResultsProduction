# DemiResults Client App

Client app workspace.

- iOS: native SwiftUI app using Apple's built-in Liquid Glass APIs.
- Android: Flutter app.

## What is included

- Home screen with AI card, promotions, popular products, consultation time and routine progress.
- Catalog with 2-column product grid.
- Favorites screen with remove/add-to-cart flow.
- Cart with quantity controls, total amount, delivery address and local card placeholder.
- Product detail bottom sheet.
- AI chat screen with product recommendations and product IDs.
- Routine screen with daily care checklist.
- Profile screen with theme switch, card binding placeholder, order history and consultation history buttons.
- iOS Liquid Glass UI built with `GlassEffectContainer` and `.glassEffect(...)`.
- Android Flutter UI with a custom glass-like fallback.

## Run iOS native Liquid Glass app

Requires Xcode with iOS 26 SDK.

```bash
cd mobile/client_app
xcodebuild \
  -workspace ios/Runner.xcworkspace \
  -scheme Runner \
  -configuration Debug \
  -destination 'platform=iOS Simulator,name=iPhone 17' \
  build
```

Install and launch on the booted simulator:

```bash
xcrun simctl install booted ~/Library/Developer/Xcode/DerivedData/Runner-*/Build/Products/Debug-iphonesimulator/Runner.app
xcrun simctl launch booted com.example.demiresultsClientApp
```

## Run Android Flutter app

Flutter SDK is required. Android still uses `lib/main.dart`.

```bash
cd mobile/client_app
flutter pub get
flutter run -d android
```

## Backend connection

The current app uses demo data so the UI can be tested immediately. Next step is to add an API client for:

- JWT auth;
- `/api/catalog/products/`;
- `/api/me/`;
- `/api/me/orders/`;
- `/api/me/consultations/`;
- cart/order creation;
- favorites persistence.

## Liquid Glass note

Apple's built-in Liquid Glass API is native SwiftUI/iOS-only and does not run on Android. The iOS Runner has been converted from Flutter-hosted UI to native SwiftUI so it can use:

```swift
GlassEffectContainer {
    Button("Shop") {}
        .glassEffect()
}
```

The SwiftUI code also keeps a fallback material style for older APIs inside helper modifiers.
