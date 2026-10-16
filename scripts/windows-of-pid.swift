// SPDX-License-Identifier: GPL-2.0-or-later
// List on-screen windows (id, bounds, title) of a process. Usage: windows-of-pid <pid>
import Foundation
import CoreGraphics
let pid = Int(CommandLine.arguments[1])!
let opts: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
let list = (CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as NSArray?) as? [[String: Any]] ?? []
for w in list where (w["kCGWindowOwnerPID"] as? Int) == pid {
    let id = w["kCGWindowNumber"] as? Int ?? -1
    let b = w["kCGWindowBounds"] as? [String: Any] ?? [:]
    let name = w["kCGWindowName"] as? String ?? ""
    let layer = w["kCGWindowLayer"] as? Int ?? 0
    print("window_id=\(id) layer=\(layer) bounds=\(b["X"] ?? 0),\(b["Y"] ?? 0) \(b["Width"] ?? 0)x\(b["Height"] ?? 0) title=\(name)")
}
