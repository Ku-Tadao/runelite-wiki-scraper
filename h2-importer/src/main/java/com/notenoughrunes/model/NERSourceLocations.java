package com.notenoughrunes.model;

import java.util.Set;
import lombok.Data;
import lombok.RequiredArgsConstructor;

@Data
@RequiredArgsConstructor
public class NERSourceLocations
{
	// a DROP_SOURCES.SOURCE value
	private final String source;
	private final Set<NERSourceLocation> locations;
}
