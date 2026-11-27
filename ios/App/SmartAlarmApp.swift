import SmartAlarmCore
import SwiftUI

@main
struct SmartAlarmApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            RootView().environment(model)
        }
    }
}

enum Stage { case home, reading, quiz, notes }

@Observable
@MainActor
final class AppModel {
    var stage: Stage = .home
    var issue: Issue?
    var questions: [PublicQuestion] = []
    var tasks: [TaskItem] = []
    var message = ""

    // Phase 0: plain defaults. Move the token to the Keychain before real use.
    var serverURL: String { get { UserDefaults.standard.string(forKey: "serverURL") ?? "" } set { UserDefaults.standard.set(newValue, forKey: "serverURL") } }
    var token: String { get { UserDefaults.standard.string(forKey: "token") ?? "" } set { UserDefaults.standard.set(newValue, forKey: "token") } }

    var client: APIClient? {
        guard let url = URL(string: serverURL), !serverURL.isEmpty else { return nil }
        return APIClient(baseURL: url, token: token)
    }

    func loadIssue() async {
        guard let client else { message = "Set the server URL in Settings."; return }
        do {
            issue = try await client.todaysIssue()
            questions = try await client.todaysQuiz()
            message = ""
        } catch APIClient.APIError.notBuiltYet {
            message = "Today's issue isn't ready yet."
        } catch {
            message = "Couldn't load today's issue."
        }
    }
}
