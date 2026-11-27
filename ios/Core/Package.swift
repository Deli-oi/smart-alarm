// swift-tools-version: 6.0
import PackageDescription

// Pure logic and networking, no AlarmKit or UI, so `swift test` runs on any Mac runner.
let package = Package(
    name: "SmartAlarmCore",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [.library(name: "SmartAlarmCore", targets: ["SmartAlarmCore"])],
    targets: [
        .target(name: "SmartAlarmCore"),
        .testTarget(name: "SmartAlarmCoreTests", dependencies: ["SmartAlarmCore"]),
    ]
)
