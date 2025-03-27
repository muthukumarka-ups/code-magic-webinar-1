//
//  Item.swift
//  Test
//
//  Created by Muralidharan Kathiresan on 27/03/2025.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
