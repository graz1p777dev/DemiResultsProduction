# DemiResults Client App

Flutter client app for iOS and Android.

## What is included

- Home screen with AI card, promotions, popular products, consultation time and routine progress.
- Catalog with 2-column product grid.
- Favorites screen with remove/add-to-cart flow.
- Cart with quantity controls, total amount, delivery address and local card placeholder.
- Product detail bottom sheet.
- AI chat screen with product recommendations and product IDs.
- Routine screen with daily care checklist.
- Profile screen with theme switch, card binding placeholder, order history and consultation history buttons.
- Cross-platform liquid glass UI built with `BackdropFilter`, translucent panels and animated bottom navigation.

## Run

Flutter SDK is required.

```bash
cd mobile/client_app
flutter create . --platforms=ios,android
flutter pub get
flutter run
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

Apple's built-in Liquid Glass API is native SwiftUI/iOS-only and does not run on Android. For the shared Flutter app, the current implementation uses a custom cross-platform liquid glass effect.

If a separate native iOS client is created later, use iOS 26+ SwiftUI APIs such as `GlassEffectContainer`, `.glassEffect(...)`, and `.buttonStyle(.glassProminent)` with availability fallbacks.
