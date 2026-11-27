import AVFoundation
import SmartAlarmCore
import SwiftUI

/// Day plan plus the opt-in Jarvis rundown. Nothing speaks unless the button is tapped.
struct NotesView: View {
    @Environment(AppModel.self) private var model
    @State private var player: AVAudioPlayer?
    @State private var status = ""

    var body: some View {
        NavigationStack {
            List {
                Section("Today") {
                    if model.tasks.isEmpty { Text("Nothing on your list.").foregroundStyle(.secondary) }
                    ForEach(model.tasks) { Text($0.title) }
                }
                Section("Jarvis") {
                    Button("Play my rundown") { Task { await play() } }
                    if !status.isEmpty { Text(status).foregroundStyle(.secondary) }
                }
            }
            .navigationTitle("Your day")
            .task {
                if let c = model.client { model.tasks = (try? await c.todaysTasks()) ?? [] }
            }
        }
    }

    private func play() async {
        guard let client = model.client else { return }
        status = "Loading..."
        do {
            let data = try await client.briefingAudio()
            try AVAudioSession.sharedInstance().setCategory(.playback)
            player = try AVAudioPlayer(data: data)
            player?.play()
            status = "Playing."
        } catch {
            status = "Couldn't play the rundown."
        }
    }
}
