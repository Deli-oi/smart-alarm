import SmartAlarmCore
import SwiftUI

struct RootView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        Group {
            switch model.stage {
            case .home: HomeView()
            case .reading: ReaderView()
            case .quiz: QuizView()
            case .notes: NotesView()
            }
        }
        .task { await model.loadIssue() }
        .onChange(of: scenePhase) { _, phase in
            // Opened from the alarm's Read button: go straight to the issue.
            if phase == .active, UserDefaults.standard.bool(forKey: "openedFromAlarm") {
                UserDefaults.standard.set(false, forKey: "openedFromAlarm")
                AlarmScheduler.cancelSafety()
                model.stage = .reading
            }
        }
    }
}

struct HomeView: View {
    @Environment(AppModel.self) private var model
    @State private var alarmStatus = ""

    var body: some View {
        @Bindable var model = model
        NavigationStack {
            Form {
                Section("Today") {
                    Button("Read today's issue") { model.stage = .reading }
                        .disabled(model.issue == nil)
                    if !model.message.isEmpty { Text(model.message).foregroundStyle(.secondary) }
                }
                Section("Alarm") {
                    Button("Set 7:00 alarm") {
                        Task {
                            guard await AlarmScheduler.authorize() else { alarmStatus = "Alarm permission denied."; return }
                            do {
                                try await AlarmScheduler.scheduleMorning(hour: 7, minute: 0)
                                alarmStatus = "Set for 7:00, with a safety alarm at 7:05."
                            } catch { alarmStatus = "Couldn't schedule: \(error.localizedDescription)" }
                        }
                    }
                    if !alarmStatus.isEmpty { Text(alarmStatus).foregroundStyle(.secondary) }
                }
                Section("Server") {
                    TextField("https://your-backend", text: $model.serverURL).textInputAutocapitalization(.never).autocorrectionDisabled()
                    SecureField("Token", text: $model.token)
                    Button("Reload") { Task { await model.loadIssue() } }
                }
            }
            .navigationTitle("Smart Alarm")
        }
    }
}
