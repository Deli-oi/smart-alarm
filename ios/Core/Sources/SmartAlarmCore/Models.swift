import Foundation

// Mirrors backend/app/models.py. Keep the two in step.

public struct Reading: Codable, Sendable, Equatable {
    public let label: String
    public let reference: String
    public let text: String
}

public struct Article: Codable, Sendable, Equatable {
    public let kind: String
    public let title: String
    public let sourceUrl: String
    public let body: String

    enum CodingKeys: String, CodingKey {
        case kind, title, body
        case sourceUrl = "source_url"
    }
}

public struct Issue: Codable, Sendable, Equatable {
    public let date: String
    public let readings: [Reading]
    public let reflection: String
    public let critical: [String]
    public let articles: [Article]

    /// All text in reading order, for pace and scroll calculations.
    public var fullText: String {
        var parts: [String] = []
        parts += critical
        parts += readings.map { "\($0.label) (\($0.reference))\n\($0.text)" }
        if !reflection.isEmpty { parts.append(reflection) }
        parts += articles.map { "\($0.title)\n\($0.body)" }
        return parts.joined(separator: "\n\n")
    }
}

public struct PublicQuestion: Codable, Sendable, Equatable, Identifiable {
    public let id: String
    public let prompt: String
    public let choices: [String]
}

public struct GateResponse: Codable, Sendable, Equatable {
    public enum Result: String, Codable, Sendable { case unlocked, retry, locked }
    public let result: Result
    public let score: Double
    public let triesUsed: Int

    enum CodingKeys: String, CodingKey {
        case result, score
        case triesUsed = "tries_used"
    }
}

public struct TaskItem: Codable, Sendable, Equatable, Identifiable {
    public let id: String
    public let date: String
    public let title: String
    public var status: String
    public var note: String
    public var pushTo: String
    public let source: String

    enum CodingKeys: String, CodingKey {
        case id, date, title, status, note, source
        case pushTo = "push_to"
    }
}
