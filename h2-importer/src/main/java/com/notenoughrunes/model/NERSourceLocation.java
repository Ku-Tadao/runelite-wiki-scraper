package com.notenoughrunes.model;

import lombok.Data;
import lombok.RequiredArgsConstructor;

@Data
@RequiredArgsConstructor
public class NERSourceLocation
{
	private final String location;

	private final boolean isMembers;

	// "x,y,plane" tiles separated by ';'
	private final String tiles;
}
