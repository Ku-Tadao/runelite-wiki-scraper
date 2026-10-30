package com.notenoughrunes.model;

import lombok.Data;
import lombok.RequiredArgsConstructor;

@Data
@RequiredArgsConstructor
public class NERSourceLocation
{
	private final String location;

	// access requirements, one per line: "quest:<name>", "started:<name>", "skill:<Skill>:<level>" or "note:<text>"
	private final String requirements;

	private final boolean isMembers;

	// "x,y,plane" tiles separated by ';'
	private final String tiles;
}
