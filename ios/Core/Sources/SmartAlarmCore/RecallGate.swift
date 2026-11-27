import Foundation

/// Local mirror of the server's gate rule, used for the offline UI. The server is authoritative.
public enum RecallGate {
    public static let passThreshold = 0.70
    public static let maxTries = 2

    public enum Outcome: Equatable, Sendable { case unlocked, retry, locked }

    public static func score(correct: Int, total: Int) -> Double {
        total == 0 ? 0 : Double(correct) / Double(total)
    }

    public static func outcome(correct: Int, total: Int, triesUsed: Int) -> Outcome {
        if score(correct: correct, total: total) >= passThreshold { return .unlocked }
        return triesUsed < maxTries ? .retry : .locked
    }
}
