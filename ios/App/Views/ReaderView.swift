import SmartAlarmCore
import SwiftUI

/// Auto-scrolling reader that fits the whole issue into the 15-minute session. Tap to pause.
struct ReaderView: View {
    @Environment(AppModel.self) private var model
    @State private var offset: CGFloat = 0
    @State private var paused = false
    @State private var contentHeight: CGFloat = 1
    @State private var secondsLeft = Int(ReaderPace.sessionMinutes * 60)
    private let tick = Timer.publish(every: 0.05, on: .main, in: .common).autoconnect()

    var body: some View {
        GeometryReader { geo in
            let text = model.issue?.fullText ?? ""
            let speed = ReaderPace.scrollSpeed(
                contentHeight: Double(contentHeight), viewportHeight: Double(geo.size.height),
                seconds: ReaderPace.sessionMinutes * 60)
            ZStack(alignment: .topTrailing) {
                Text(text)
                    .font(.system(size: 22, design: .serif))
                    .lineSpacing(8)
                    .padding(24)
                    .frame(width: geo.size.width, alignment: .leading)
                    .background(GeometryReader { g in
                        Color.clear.onAppear { contentHeight = g.size.height }
                    })
                    .offset(y: -offset)
                    .frame(maxHeight: .infinity, alignment: .top)
                    .clipped()
                    .onReceive(tick) { _ in
                        guard !paused else { return }
                        offset = min(offset + CGFloat(speed) * 0.05, max(contentHeight - geo.size.height, 0))
                    }
                Text(timeString).monospacedDigit().padding(8).background(.thinMaterial, in: Capsule()).padding()
            }
            .contentShape(Rectangle())
            .onTapGesture { paused.toggle() }
            .overlay(alignment: .bottom) {
                Button("Done reading: start recall") { model.stage = .quiz }
                    .buttonStyle(.borderedProminent).padding()
            }
        }
        .task {
            while secondsLeft > 0 {
                try? await Task.sleep(for: .seconds(1))
                if !paused { secondsLeft -= 1 }
            }
        }
    }

    private var timeString: String {
        String(format: "%d:%02d", secondsLeft / 60, secondsLeft % 60)
    }
}
