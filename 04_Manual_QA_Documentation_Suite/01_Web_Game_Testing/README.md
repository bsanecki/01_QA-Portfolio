# Manual QA Documentation - Web Game

## Project Overview

This project contains manual QA documentation for **The Dig Game**, a browser-based game available on itch.io.

The goal was to evaluate core gameplay functionality, identify defects, document test results, and provide video evidence for reported issues.

**Game:** The Dig Game  
**Game URL:** https://louisdesimone.itch.io/the-dig-game  
**Project Type:** Independent QA Portfolio Project  
**Testing Type:** Manual Functional Testing  
**Test Environment:** Chromium on Fedora Linux 44  
**Test Period:** 30-31 July 2026

## Project Contents

### 1. Test Documentation

`The_Dig_Game_Manual_QA_Documentation.xlsx`

The Excel workbook contains three worksheets:

- **Test Info** - project information, test scope, approach, environment, and test summary.
- **Test Cases** - test scenarios, steps, expected and actual results, execution statuses, and related bug IDs.
- **Bug Reports** - detailed defect descriptions, reproduction steps, expected and actual results, and evidence links.

### 2. Evidence Recordings

The `evidence/` directory contains video recordings documenting the four reported defects.

| Recording | Description |
|---|---|
| `bug_recording_01_floating_stones.mp4` | Stones remain suspended after surrounding terrain is removed. |
| `bug_recording_02_glider_flickering.mp4` | The glider flickers or shifts position when looking downward. |
| `bug_recording_03_shovel_clipping.mp4` | The shovel clips through the wall of a dug hole. |
| `bug_recording_04_fence_collision.mp4` | The character passes through a fence. |

## Test Coverage

The test cases cover the following areas:

- Movement and controls
- Collision detection
- Digging mechanics
- Physics and environment
- Gliding mechanics
- Camera and perspective
- Visual defects and clipping
- Object interaction
- Game UI, input handling, stability, and edge cases

## Reported Defects

Four unique defects were documented:

1. Floating stones after digging.
2. Glider flickering and incorrect positioning.
3. Shovel clipping through terrain.
4. Character passing through a fence.

Each defect has a corresponding bug ID and supporting video evidence.

## Tools and Technologies

- Chromium
- Fedora Linux 44
- Microsoft Excel / LibreOffice Calc
- Loom for video evidence

## Project Purpose

This project demonstrates practical manual QA documentation skills, including test case design, functional and exploratory testing, defect reporting, traceability between test cases and bugs, and evidence collection.
