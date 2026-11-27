import Foundation
import Testing
@testable import SmartAlarmCore

@Suite struct ReaderPaceTests {
    @Test func countsWords() {
        #expect(ReaderPace.wordCount("one two\nthree   four") == 4)
    }

    @Test func fifteenMinuteIssueIsAboutTwoThousandEightHundredWords() {
        let text = Array(repeating: "word", count: 2850).joined(separator: " ")
        let seconds = ReaderPace.readingSeconds(text)
        #expect(seconds > 800 && seconds < 1000)
    }

    @Test func fittedPaceIsClamped() {
        let short = Array(repeating: "w", count: 300).joined(separator: " ")
        #expect(ReaderPace.fittedWordsPerMinute(short) == 120)
    }

    @Test func scrollSpeedUsesTravelDistance() {
        #expect(ReaderPace.scrollSpeed(contentHeight: 1000, viewportHeight: 400, seconds: 60) == 10)
        #expect(ReaderPace.scrollSpeed(contentHeight: 300, viewportHeight: 400, seconds: 60) == 0)
    }
}

@Suite struct RecallGateTests {
    @Test func unlocksAtSeventyPercent() {
        #expect(RecallGate.outcome(correct: 7, total: 10, triesUsed: 1) == .unlocked)
    }

    @Test func retryThenLocked() {
        #expect(RecallGate.outcome(correct: 6, total: 10, triesUsed: 1) == .retry)
        #expect(RecallGate.outcome(correct: 6, total: 10, triesUsed: 2) == .locked)
    }
}

@Suite struct DecodingTests {
    @Test func decodesGateResponse() throws {
        let json = #"{"result":"unlocked","score":0.8,"tries_used":1}"#.data(using: .utf8)!
        let r = try JSONDecoder().decode(GateResponse.self, from: json)
        #expect(r.result == .unlocked && r.triesUsed == 1)
    }

    @Test func decodesIssue() throws {
        let json = """
        {"date":"2026-11-27","readings":[{"label":"Gospel","reference":"Lk 1:1","text":"t"}],
         "reflection":"r","critical":[],
         "articles":[{"kind":"research","title":"T","source_url":"u","body":"b"}]}
        """.data(using: .utf8)!
        let issue = try JSONDecoder().decode(Issue.self, from: json)
        #expect(issue.articles.first?.sourceUrl == "u")
        #expect(issue.fullText.contains("Gospel"))
    }

    @Test func decodesDayPlan() throws {
        let json = """
        {"date":"2026-11-27","events":[{"start":"12:00","end":"13:30","title":"Work","location":"",
          "all_day":false,"overlaps":true}],
         "mail":[{"sender":"A","subject":"Hi"}],"errors":["mail: GMAIL_USER / GMAIL_APP_PASSWORD not set"]}
        """.data(using: .utf8)!
        let day = try JSONDecoder().decode(DayPlan.self, from: json)
        #expect(day.events.first?.overlaps == true)
        #expect(day.errors.count == 1)
    }

    @Test func requestCarriesBearerToken() {
        let c = APIClient(baseURL: URL(string: "https://example.com")!, token: "abc")
        #expect(c.request("issue/today").value(forHTTPHeaderField: "Authorization") == "Bearer abc")
    }
}
