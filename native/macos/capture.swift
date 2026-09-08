import Foundation
import AVFoundation
import CoreMedia
import ScreenCaptureKit

final class RecordingDelegate: NSObject, SCRecordingOutputDelegate {
    func recordingOutputDidStartRecording(
        _ recordingOutput: SCRecordingOutput
    ) {
        print("Recording started...")
    }

    func recordingOutputDidFinishRecording(
        _ recordingOutput: SCRecordingOutput
    ) {
        print("Recording finished.")
    }

    func recordingOutput(
        _ recordingOutput: SCRecordingOutput,
        didFailWithError error: Error
    ) {
        print("Recording failed: \(error)")
    }
}

@main
struct CaptureTest {
    static func main() async {
        do {
            guard CommandLine.arguments.count >= 2 else {
                print("Usage: capture <output_path>")
                return
            }

            let outputURL = URL(
                fileURLWithPath: CommandLine.arguments[1]
            )

            let content = try await SCShareableContent.excludingDesktopWindows(
                false,
                onScreenWindowsOnly: true
            )

            guard let display = content.displays.first else {
                print("No display found.")
                return
            }

            let filter = SCContentFilter(
                display: display,
                excludingWindows: []
            )

            let streamConfiguration = SCStreamConfiguration()

            streamConfiguration.width = display.width
            streamConfiguration.height = display.height

            streamConfiguration.minimumFrameInterval = CMTime(
                value: 1,
                timescale: 30
            )

            streamConfiguration.capturesAudio = true
            streamConfiguration.sampleRate = 48_000
            streamConfiguration.channelCount = 2
            streamConfiguration.excludesCurrentProcessAudio = true

            try? FileManager.default.removeItem(
                at: outputURL
            )

            let recordingConfiguration = SCRecordingOutputConfiguration()

            recordingConfiguration.outputURL = outputURL
            recordingConfiguration.outputFileType = .mov
            recordingConfiguration.videoCodecType = .h264

            let recordingDelegate = RecordingDelegate()

            let recordingOutput = SCRecordingOutput(
                configuration: recordingConfiguration,
                delegate: recordingDelegate
            )

            let stream = SCStream(
                filter: filter,
                configuration: streamConfiguration,
                delegate: nil
            )

            try stream.addRecordingOutput(
                recordingOutput
            )

            try await stream.startCapture()

            print("Press ENTER to stop.")
            _ = readLine()

            try await stream.stopCapture()

            print("Saved to:")
            print(outputURL.path)

        } catch {
            print("Error: \(error)")
        }
    }
}