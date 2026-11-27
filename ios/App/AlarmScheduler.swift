import AlarmKit
import AppIntents
import SwiftUI

// All AlarmKit use lives in this one file: the API is new and may change.
// Written without a compiler on hand; the CI build is the first real check.

struct WakeMetadata: AlarmMetadata {}

/// Runs when the user taps the alarm's custom button. Opens the app, which takes over ringing.
struct OpenIssueIntent: LiveActivityIntent {
    static let title: LocalizedStringResource = "Open today's issue"
    static let openAppWhenRun = true

    @Parameter(title: "Alarm ID") var alarmID: String

    init() { self.alarmID = "" }
    init(alarmID: String) { self.alarmID = alarmID }

    func perform() async throws -> some IntentResult {
        UserDefaults.standard.set(true, forKey: "openedFromAlarm")
        return .result()
    }
}

struct StopIntent: LiveActivityIntent {
    static let title: LocalizedStringResource = "Stop alarm"

    @Parameter(title: "Alarm ID") var alarmID: String

    init() { self.alarmID = "" }
    init(alarmID: String) { self.alarmID = alarmID }

    func perform() async throws -> some IntentResult {
        try? AlarmManager.shared.stop(id: UUID(uuidString: alarmID) ?? UUID())
        return .result()
    }
}

enum AlarmScheduler {
    private static let mainKey = "mainAlarmID"
    private static let safetyKey = "safetyAlarmID"

    static func authorize() async -> Bool {
        switch AlarmManager.shared.authorizationState {
        case .authorized: return true
        case .notDetermined:
            return (try? await AlarmManager.shared.requestAuthorization()) == .authorized
        default: return false
        }
    }

    /// Schedules the main alarm plus a safety alarm a few minutes later, in case the first is slept through.
    static func scheduleMorning(hour: Int, minute: Int, safetyMinutesLater: Int = 10) async throws {
        try await cancelAll()
        let mainID = UUID()
        try await schedule(id: mainID, hour: hour, minute: minute, title: "Wake up", showRead: true)
        UserDefaults.standard.set(mainID.uuidString, forKey: mainKey)

        let total = hour * 60 + minute + safetyMinutesLater
        let safetyID = UUID()
        try await schedule(id: safetyID, hour: (total / 60) % 24, minute: total % 60, title: "Still asleep?", showRead: true)
        UserDefaults.standard.set(safetyID.uuidString, forKey: safetyKey)
    }

    /// Called once the issue is opened, so the safety alarm doesn't ring.
    static func cancelSafety() {
        guard let s = UserDefaults.standard.string(forKey: safetyKey), let id = UUID(uuidString: s) else { return }
        try? AlarmManager.shared.cancel(id: id)
    }

    static func cancelAll() async throws {
        for key in [mainKey, safetyKey] {
            if let s = UserDefaults.standard.string(forKey: key), let id = UUID(uuidString: s) {
                try? AlarmManager.shared.cancel(id: id)
            }
        }
    }

    private static func schedule(id: UUID, hour: Int, minute: Int, title: String, showRead: Bool) async throws {
        let time = Alarm.Schedule.Relative.Time(hour: hour, minute: minute)
        let schedule = Alarm.Schedule.relative(.init(time: time, repeats: .never))

        let stop = AlarmButton(text: "Stop", textColor: .white, systemImageName: "stop.circle")
        let read = AlarmButton(text: "Read", textColor: .white, systemImageName: "book")
        let alert = AlarmPresentation.Alert(
            title: LocalizedStringResource(stringLiteral: title),
            stopButton: stop,
            secondaryButton: showRead ? read : nil,
            secondaryButtonBehavior: showRead ? .custom : nil
        )
        let attributes = AlarmAttributes(
            presentation: AlarmPresentation(alert: alert),
            metadata: WakeMetadata(),
            tintColor: .blue
        )
        let config = AlarmManager.AlarmConfiguration.alarm(
            schedule: schedule,
            attributes: attributes,
            stopIntent: StopIntent(alarmID: id.uuidString),
            secondaryIntent: OpenIssueIntent(alarmID: id.uuidString)
        )
        _ = try await AlarmManager.shared.schedule(id: id, configuration: config)
    }
}
