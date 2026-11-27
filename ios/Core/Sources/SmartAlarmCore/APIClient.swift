import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

public struct APIClient: Sendable {
    public let baseURL: URL
    public let token: String
    private let session: URLSession

    public init(baseURL: URL, token: String, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.token = token
        self.session = session
    }

    public enum APIError: Error, Equatable {
        case notBuiltYet  // 404: today's issue hasn't been built; use the cached copy
        case unauthorized
        case server(Int)
    }

    func request(_ path: String, method: String = "GET", body: Data? = nil) -> URLRequest {
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = method
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        if let body {
            req.httpBody = body
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        return req
    }

    private func send<T: Decodable>(_ req: URLRequest, as type: T.Type) async throws -> T {
        let (data, resp) = try await session.data(for: req)
        let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
        switch code {
        case 200..<300: return try JSONDecoder().decode(T.self, from: data)
        case 401: throw APIError.unauthorized
        case 404: throw APIError.notBuiltYet
        default: throw APIError.server(code)
        }
    }

    public func todaysIssue() async throws -> Issue {
        try await send(request("issue/today"), as: Issue.self)
    }

    public func todaysQuiz() async throws -> [PublicQuestion] {
        try await send(request("quiz/today"), as: [PublicQuestion].self)
    }

    public func submit(answers: [String: Int]) async throws -> GateResponse {
        let body = try JSONEncoder().encode(["answers": answers])
        return try await send(request("quiz/submit", method: "POST", body: body), as: GateResponse.self)
    }

    public func todaysTasks() async throws -> [TaskItem] {
        try await send(request("tasks/today"), as: [TaskItem].self)
    }

    public func briefingText() async throws -> String {
        struct B: Decodable { let text: String }
        return try await send(request("jarvis/briefing"), as: B.self).text
    }

    /// Opt-in spoken briefing (mp3 bytes). Only called when the user taps Jarvis.
    public func briefingAudio() async throws -> Data {
        let (data, resp) = try await session.data(for: request("jarvis/speak"))
        guard (resp as? HTTPURLResponse)?.statusCode == 200 else { throw APIError.server(0) }
        return data
    }
}
