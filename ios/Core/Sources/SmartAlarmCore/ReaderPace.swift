import Foundation

/// Reading pace for the auto-scrolling newsletter.
public enum ReaderPace {
    public static let defaultWordsPerMinute = 190.0
    public static let sessionMinutes = 15.0

    public static func wordCount(_ text: String) -> Int {
        text.split(whereSeparator: { $0.isWhitespace }).count
    }

    /// Seconds to read `text` at the given pace.
    public static func readingSeconds(_ text: String, wordsPerMinute: Double = defaultWordsPerMinute) -> Double {
        Double(wordCount(text)) / wordsPerMinute * 60.0
    }

    /// Points per second to scroll so a page of `contentHeight` takes `seconds` to pass.
    public static func scrollSpeed(contentHeight: Double, viewportHeight: Double, seconds: Double) -> Double {
        let travel = max(contentHeight - viewportHeight, 0)
        guard seconds > 0 else { return 0 }
        return travel / seconds
    }

    /// Pace that fits `text` into the 15-minute session, clamped to a readable range.
    public static func fittedWordsPerMinute(_ text: String) -> Double {
        let fitted = Double(wordCount(text)) / sessionMinutes
        return min(max(fitted, 120), 260)
    }
}
