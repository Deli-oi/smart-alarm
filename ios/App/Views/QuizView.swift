import SmartAlarmCore
import SwiftUI

/// The recall gate. The server grades; the phone never sees the answers.
struct QuizView: View {
    @Environment(AppModel.self) private var model
    @State private var answers: [String: Int] = [:]
    @State private var result: GateResponse?
    @State private var busy = false

    var body: some View {
        NavigationStack {
            List {
                ForEach(model.questions) { q in
                    Section(q.prompt) {
                        ForEach(q.choices.indices, id: \.self) { i in
                            Button {
                                answers[q.id] = i
                            } label: {
                                HStack {
                                    Text(q.choices[i])
                                    Spacer()
                                    if answers[q.id] == i { Image(systemName: "checkmark") }
                                }
                            }
                        }
                    }
                }
                Section {
                    Button("Submit") { Task { await submit() } }
                        .disabled(busy || answers.count < model.questions.count)
                    if let r = result { Text(summary(r)) }
                }
            }
            .navigationTitle("Recall")
        }
    }

    private func submit() async {
        guard let client = model.client else { return }
        busy = true
        defer { busy = false }
        guard let r = try? await client.submit(answers: answers) else { return }
        result = r
        switch r.result {
        case .unlocked: model.stage = .notes
        case .retry: answers = [:]
        case .locked: break  // emergency skip is logged in a later phase
        }
    }

    private func summary(_ r: GateResponse) -> String {
        let pct = Int((r.score * 100).rounded())
        switch r.result {
        case .unlocked: return "\(pct)%. Unlocked."
        case .retry: return "\(pct)%. Need 70%. One more try."
        case .locked: return "Out of tries."
        }
    }
}
