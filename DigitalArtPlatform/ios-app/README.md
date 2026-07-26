# iOS App

Native iOS application for the Digital Art Platform built with SwiftUI.

## Features

- **SwiftUI**: Modern declarative UI framework
- **MVVM Architecture**: Clean separation of concerns
- **Async/Await**: Modern concurrency
- **Core Data**: Local data persistence
- **Combine Framework**: Reactive programming
- **PhotoKit**: Access to user's photo library
- **Biometric Authentication**: Face ID / Touch ID
- **Dark Mode**: Full dark mode support
- **Offline Mode**: Cache and sync when online
- **Widget Support**: Home screen widgets
- **Push Notifications**: Real-time updates

## Requirements

- iOS 16.0+
- Xcode 15.0+
- Swift 5.9+
- CocoaPods or Swift Package Manager

## Getting Started

### 1. Open Project

```bash
cd ios-app
open DigitalArtPlatform.xcodeproj
```

### 2. Install Dependencies

Using Swift Package Manager (recommended):
- Dependencies are automatically managed by Xcode
- No additional setup required

Or using CocoaPods:
```bash
pod install
open DigitalArtPlatform.xcworkspace
```

### 3. Configure Environment

Create `Config.swift` from template:
```bash
cp Config.swift.example Config.swift
# Edit Config.swift with your API endpoint
```

### 4. Build and Run

- Select target device or simulator
- Press `Cmd + R` to build and run

## Project Structure

```
ios-app/
├── DigitalArtPlatform/
│   ├── App/
│   │   ├── DigitalArtPlatformApp.swift  # App entry point
│   │   └── Config.swift                  # Configuration
│   │
│   ├── Models/                          # Data models
│   │   ├── Artwork.swift
│   │   ├── Collection.swift
│   │   ├── User.swift
│   │   └── Device.swift
│   │
│   ├── ViewModels/                      # MVVM ViewModels
│   │   ├── ArtworkListViewModel.swift
│   │   ├── ArtworkDetailViewModel.swift
│   │   ├── CollectionViewModel.swift
│   │   └── AuthViewModel.swift
│   │
│   ├── Views/                           # SwiftUI Views
│   │   ├── Artwork/
│   │   │   ├── ArtworkListView.swift
│   │   │   ├── ArtworkDetailView.swift
│   │   │   └── ArtworkCardView.swift
│   │   ├── Collection/
│   │   │   ├── CollectionListView.swift
│   │   │   └── CollectionDetailView.swift
│   │   ├── Device/
│   │   │   ├── DeviceListView.swift
│   │   │   └── DeviceControlView.swift
│   │   ├── Profile/
│   │   │   └── ProfileView.swift
│   │   └── Auth/
│   │       ├── LoginView.swift
│   │       └── RegisterView.swift
│   │
│   ├── Services/                        # Business logic
│   │   ├── APIService.swift             # API client
│   │   ├── AuthService.swift            # Authentication
│   │   ├── ImageService.swift           # Image handling
│   │   ├── CacheService.swift           # Caching
│   │   └── SyncService.swift            # Data synchronization
│   │
│   ├── Networking/                      # Network layer
│   │   ├── APIClient.swift
│   │   ├── Endpoint.swift
│   │   └── NetworkError.swift
│   │
│   ├── Persistence/                     # Core Data
│   │   ├── PersistenceController.swift
│   │   └── DigitalArtPlatform.xcdatamodeld
│   │
│   ├── Utilities/                       # Helpers
│   │   ├── Extensions/
│   │   ├── Constants.swift
│   │   └── Helpers.swift
│   │
│   └── Resources/                       # Assets
│       ├── Assets.xcassets
│       └── Localizable.strings
│
├── DigitalArtPlatformTests/            # Unit tests
├── DigitalArtPlatformUITests/          # UI tests
├── DigitalArtPlatformWidget/           # Widget extension
└── README.md
```

## Architecture

### MVVM Pattern

```swift
// Model
struct Artwork: Identifiable, Codable {
    let id: Int
    let title: String
    let thumbnailURL: String
    let artist: Artist?
}

// ViewModel
@MainActor
class ArtworkListViewModel: ObservableObject {
    @Published var artworks: [Artwork] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let artworkService: ArtworkService
    
    init(artworkService: ArtworkService = .shared) {
        self.artworkService = artworkService
    }
    
    func loadArtworks() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            artworks = try await artworkService.fetchArtworks()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View
struct ArtworkListView: View {
    @StateObject private var viewModel = ArtworkListViewModel()
    
    var body: some View {
        List(viewModel.artworks) { artwork in
            ArtworkCardView(artwork: artwork)
        }
        .task {
            await viewModel.loadArtworks()
        }
    }
}
```

### Networking

API client with automatic token refresh:

```swift
class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "https://api.digitalartplatform.com/api/v1"
    
    func request<T: Decodable>(
        _ endpoint: Endpoint,
        method: HTTPMethod = .get,
        body: Encodable? = nil
    ) async throws -> T {
        var request = URLRequest(url: endpoint.url)
        request.httpMethod = method.rawValue
        
        // Add auth token
        if let token = AuthService.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Add body
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        // Handle 401 - refresh token
        if httpResponse.statusCode == 401 {
            try await AuthService.shared.refreshToken()
            return try await self.request(endpoint, method: method, body: body)
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.statusCode(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

### Persistence

Core Data for offline storage:

```swift
class PersistenceController {
    static let shared = PersistenceController()
    
    let container: NSPersistentContainer
    
    init() {
        container = NSPersistentContainer(name: "DigitalArtPlatform")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data failed to load: \(error.localizedDescription)")
            }
        }
    }
    
    func save() {
        let context = container.viewContext
        
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save context: \(error)")
            }
        }
    }
}
```

## Key Features

### Authentication

```swift
class AuthService {
    static let shared = AuthService()
    
    @Published var isAuthenticated = false
    private(set) var accessToken: String?
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await APIClient.shared.request(
            .login,
            method: .post,
            body: LoginRequest(email: email, password: password)
        )
        
        accessToken = response.accessToken
        storeRefreshToken(response.refreshToken)
        isAuthenticated = true
    }
    
    func logout() {
        accessToken = nil
        clearRefreshToken()
        isAuthenticated = false
    }
}
```

### Image Caching

```swift
class ImageCache {
    static let shared = ImageCache()
    private let cache = NSCache<NSString, UIImage>()
    
    func get(url: String) -> UIImage? {
        return cache.object(forKey: url as NSString)
    }
    
    func set(url: String, image: UIImage) {
        cache.setObject(image, forKey: url as NSString)
    }
}

// SwiftUI view extension
extension Image {
    init(url: String) {
        if let cached = ImageCache.shared.get(url: url) {
            self.init(uiImage: cached)
        } else {
            self.init(systemName: "photo")
            // Load asynchronously
        }
    }
}
```

### Biometric Authentication

```swift
import LocalAuthentication

func authenticateWithBiometrics() async -> Bool {
    let context = LAContext()
    var error: NSError?
    
    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
        return false
    }
    
    do {
        return try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Authenticate to access your artworks"
        )
    } catch {
        return false
    }
}
```

### Photo Upload

```swift
import PhotosUI

struct PhotoUploadView: View {
    @State private var selectedPhoto: PhotosPickerItem?
    
    var body: some View {
        PhotosPicker(
            selection: $selectedPhoto,
            matching: .images
        ) {
            Label("Upload Photo", systemImage: "photo.on.rectangle.angled")
        }
        .onChange(of: selectedPhoto) { newValue in
            Task {
                if let data = try? await newValue?.loadTransferable(type: Data.self) {
                    await uploadPhoto(data)
                }
            }
        }
    }
}
```

## Testing

### Unit Tests

```swift
import XCTest
@testable import DigitalArtPlatform

class ArtworkServiceTests: XCTestCase {
    var sut: ArtworkService!
    var mockAPI: MockAPIClient!
    
    override func setUp() {
        super.setUp()
        mockAPI = MockAPIClient()
        sut = ArtworkService(apiClient: mockAPI)
    }
    
    func testFetchArtworks() async throws {
        // Given
        let expectedArtworks = [
            Artwork(id: 1, title: "Test", thumbnailURL: "url", artist: nil)
        ]
        mockAPI.artworksToReturn = expectedArtworks
        
        // When
        let artworks = try await sut.fetchArtworks()
        
        // Then
        XCTAssertEqual(artworks, expectedArtworks)
        XCTAssertEqual(mockAPI.fetchArtworksCallCount, 1)
    }
}
```

### UI Tests

```swift
import XCTest

class ArtworkListUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testArtworkListDisplaysArtworks() {
        // Navigate to artwork list
        app.tabBars.buttons["Artworks"].tap()
        
        // Wait for artworks to load
        let firstArtwork = app.cells.firstMatch
        XCTAssertTrue(firstArtwork.waitForExistence(timeout: 5))
        
        // Tap artwork
        firstArtwork.tap()
        
        // Verify detail view appears
        XCTAssertTrue(app.navigationBars["Artwork Detail"].exists)
    }
}
```

## Building for Release

### 1. Update Version

Update version in Xcode:
- Select project in navigator
- General tab → Identity section
- Update Version and Build

### 2. Configure Signing

- Select project → Signing & Capabilities
- Select your team
- Configure provisioning profile

### 3. Archive

```
Product → Archive
```

### 4. Submit to App Store

- Xcode → Window → Organizer
- Select archive
- Distribute App → App Store Connect

## App Store Requirements

### Screenshots

Required sizes:
- 6.7" (iPhone 14 Pro Max): 1290 x 2796
- 6.5" (iPhone 11 Pro Max): 1242 x 2688
- 5.5" (iPhone 8 Plus): 1242 x 2208
- 12.9" iPad Pro: 2048 x 2732

### Privacy

Privacy manifest required for:
- Network requests
- Photo library access
- Biometric authentication

Add `PrivacyInfo.xcprivacy` file.

### App Store Connect

Required information:
- App description
- Keywords
- Support URL
- Privacy policy URL
- Screenshots
- App icon (1024x1024)

## Performance

### Optimization Tips

1. **Image Loading**: Use progressive JPEG and WebP
2. **Memory**: Release images when not visible
3. **Network**: Use HTTP/2 and compression
4. **Battery**: Minimize background tasks
5. **Launch Time**: Lazy load heavy resources

### Instruments

Profile with Xcode Instruments:
- Time Profiler
- Allocations
- Leaks
- Network
- Energy Log

## Accessibility

```swift
struct ArtworkCard: View {
    let artwork: Artwork
    
    var body: some View {
        VStack {
            AsyncImage(url: URL(string: artwork.thumbnailURL))
                .accessibilityLabel(artwork.title)
            
            Text(artwork.title)
                .font(.headline)
            
            Button("Favorite") {
                // ...
            }
            .accessibilityLabel("Favorite \(artwork.title)")
            .accessibilityHint("Double tap to add to favorites")
        }
    }
}
```

## Localization

Support multiple languages:

```swift
// Localizable.strings
"artwork.favorite" = "Favorite";
"artwork.unfavorite" = "Unfavorite";

// In code
Text("artwork.favorite")
```

## Contributing

See [Coding Standards](../documentation/CODING_STANDARDS.md) for Swift code style guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file for details.
