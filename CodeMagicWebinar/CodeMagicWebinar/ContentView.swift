//
//  ContentView.swift
//  CodeMagicWebinar
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            HomeView()
        }
        .padding()
    }
}

struct HomeView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Home View!")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
