# Dancing with SAR
### Understanding Earth's Changing Surface Through Radar Observations

**Powered by Earth Twin Engine (ETE) · TerraTrace**

> Earth's surface is never static. It expands, contracts, floods, deforms, grows, and transforms. Dancing with SAR makes these changes visible through time using Synthetic Aperture Radar observations from the NASA-ISRO NISAR mission.

---

## 1. Project Overview

**Dancing with SAR** is an interactive geospatial and spatiotemporal visualization platform designed to track, analyze, and communicate changes occurring across Earth's surface using Synthetic Aperture Radar (SAR) observations.

Developed around the NASA-ISRO Synthetic Aperture Radar (NISAR) mission, the platform aims to transform complex radar measurements into accessible visual representations of environmental and geographical change.

The application enables users to explore selected geographic regions, examine radar observations acquired at different points in time, compare surface conditions, and visualize changes through an interactive Earth interface and generalized temporal timeline.

Rather than treating satellite observations as isolated images, Dancing with SAR organizes them into a continuous spatiotemporal representation of Earth's changing surface.

The project builds upon the geospatial visualization and temporal data architecture developed for **Avani**, extending its capabilities from atmospheric observation and extreme-weather anomaly tracking toward radar-based Earth surface monitoring.

### Project Identity

| Attribute | Description |
|---|---|
| Project Name | Dancing with SAR |
| Core Engine | Earth Twin Engine (ETE) |
| Scientific Subsystem | TerraTrace |
| Primary Data Source | NASA-ISRO NISAR |
| Scientific Domain | Radar Remote Sensing and Earth Observation |
| Primary Focus | Spatiotemporal Surface Change Detection |
| Visualization | Interactive 3D Earth and Temporal Layers |
| Development Approach | Reuse and extend Avani's existing geospatial infrastructure |

---

## 2. The Problem

Earth is continuously undergoing natural and human-induced transformations.

These include:

- Floodplains expanding and contracting.
- Wetlands experiencing degradation or recovery.
- Forest structures changing due to deforestation and wildfires.
- Agricultural landscapes changing through cultivation and soil-moisture variations.
- Glaciers and sea ice changing over time.
- Ground surfaces deforming due to earthquakes, subsidence, and other geological processes.

Although satellite observations provide valuable information about these phenomena, interpreting changes across multiple observations and time periods is not always straightforward.

Traditional satellite-image viewers often present observations as individual images. This makes it difficult for non-specialists and decision-makers to understand how a geographical region evolves over time.

Synthetic Aperture Radar provides an important opportunity to address this limitation.

Unlike optical satellite instruments, SAR actively emits microwave signals and measures the energy reflected from Earth's surface. It can collect observations independently of sunlight and is capable of operating through cloud cover.

However, SAR observations are fundamentally different from conventional optical imagery. Their interpretation requires an understanding of radar backscatter, polarization, surface roughness, dielectric properties, and, for interferometric applications, phase information.

**The challenge is therefore not simply displaying radar imagery. It is translating radar observations into meaningful representations of geographical change.**

---

## 3. Our Approach

Dancing with SAR approaches this challenge through a combination of geospatial data management, temporal analysis, radar-specific processing, and interactive visualization.

The central idea is to represent Earth's surface as a collection of geographically located observations evolving through time.

Every observation is associated with:

- Geographic location or spatial footprint.
- Acquisition timestamp.
- Radar acquisition characteristics.
- Polarization information, where applicable.
- Backscatter or other relevant measurement values.
- Processing and quality metadata.

These observations are organized into temporal sequences and spatial layers.

Users can then explore how a selected region changes across successive observations.

### Core Workflow

1. **Study Area Selection**

   Select a geographic region of interest, such as a flood-prone region, wetland, agricultural landscape, forest, or earthquake-affected area.

2. **SAR Data Acquisition**

   Retrieve suitable NISAR observations using the data resources provided by NASA and the challenge.

3. **Data Preparation**

   Decode the selected product, inspect its metadata, prepare its spatial reference, and extract the measurements needed for visualization.

4. **Spatial Registration**

   Associate observations with their geographic coordinates and spatial footprints.

5. **Temporal Organization**

   Organize observations according to their acquisition timestamps to create a chronological representation of the study area.

6. **Scientific Analysis**

   Apply appropriate SAR processing and comparison techniques to identify changes between observations.

7. **Visualization**

   Display the observations, derived analytical layers, and temporal changes on an interactive Earth interface.

8. **Interpretation**

   Communicate the observed changes and possible physical drivers through contextual information and visual storytelling.

---

## 4. Earth Twin Engine (ETE)

Earth Twin Engine is the underlying application and visualization architecture intended to support multiple Earth-observation domains.

The engine separates reusable geospatial and temporal infrastructure from domain-specific scientific processing.

This distinction is important because different Earth-observation systems may use entirely different scientific datasets while sharing common spatial, temporal, and visualization requirements.

For example:

- Avani uses atmospheric observations and weather-related variables.
- Dancing with SAR uses radar observations and surface-related measurements.

Both applications require geographic positioning, temporal organization, spatial data layers, and interactive visualization.

Instead of building separate infrastructure for every scientific domain, ETE provides a shared foundation.

### 4.1 Shared Engine Capabilities

**Spatial System**

- Geographic coordinate handling.
- Latitude-longitude positioning.
- Spatial region selection.
- Geospatial layer management.
- Support for gridded and raster-based observations.

**Temporal System**

- Acquisition timestamp management.
- Generalized timeline.
- Temporal indexing.
- Observation sequencing.
- Before-and-after comparisons.
- Time-dependent visualization.

**Data System**

- Domain-specific data ingestion.
- Data normalization.
- Metadata management.
- Spatial and temporal association.
- Scientific data adapters.

**Visualization System**

- Interactive Earth visualization.
- Spatial overlays.
- Temporal playback.
- Layer visibility controls.
- Comparative visualization.
- Scientific visualization components.

### 4.2 Domain-Specific Processing

ETE does not assume that every Earth-observation dataset has the same structure or scientific meaning.

Instead, individual scientific subsystems provide their own data interpretation and processing capabilities.

| Subsystem | Data Domain | Scientific Purpose |
|---|---|---|
| Avani | Atmospheric observations | Extreme-weather anomaly tracking |
| TerraTrace | SAR and surface observations | Earth surface change monitoring |

This separation allows the shared engine to evolve without coupling it to one scientific domain.

---

## 5. TerraTrace — SAR Observation and Change Analysis

TerraTrace is the scientific subsystem responsible for interpreting radar observations and representing changes occurring across Earth's surface.

It provides the domain-specific capabilities required by Dancing with SAR.

### 5.1 SAR Observation Management

TerraTrace organizes radar observations into structured spatial and temporal records.

An observation may contain:

- Acquisition date and time.
- Geographic footprint.
- Radar frequency and polarization metadata.
- Backscatter measurements.
- Product identifiers.
- Spatial resolution and coordinate reference information.
- Relevant processing metadata.

The exact fields depend on the NISAR product selected.

### 5.2 Backscatter Visualization

SAR backscatter represents the radar energy reflected toward the instrument.

It provides information influenced by surface roughness, geometry, moisture, vegetation structure, and other properties.

TerraTrace aims to visualize backscatter measurements through interpretable raster layers.

Users should be able to:

- Explore radar intensity.
- Compare observations acquired on different dates.
- Inspect different available polarization channels.
- Identify areas showing substantial changes in radar response.

Backscatter changes must not automatically be interpreted as a particular physical event. They require contextual interpretation and, where appropriate, additional datasets.

### 5.3 Temporal Change Detection

One of the primary capabilities of TerraTrace is identifying differences between radar observations acquired at different times.

For a selected region, the system can compare observations from two or more acquisition dates.

A simplified comparison can be represented as:

\[
\Delta B(x,y,t)=B(x,y,t_2)-B(x,y,t_1)
\]

Where:

- \(B\) represents a suitable backscatter measurement.
- \(x,y\) represent spatial coordinates.
- \(t_1,t_2\) represent acquisition times.

The resulting difference layer can highlight locations where radar responses have changed.

This is an analytical starting point rather than a universal change-detection method. Appropriate calibration, radiometric normalization, spatial alignment, and product-specific processing are necessary before interpreting differences scientifically.

### 5.4 Surface Change Interpretation

TerraTrace will initially focus on one selected phenomenon and provide the processing and visualization needed to communicate it.

Potential applications include:

- Flood inundation monitoring.
- Wetland expansion and contraction.
- Forest disturbance.
- Agricultural surface changes.
- Soil-moisture-related changes.
- Surface deformation, where suitable interferometric products are available.

The system should distinguish between directly measured radar changes and inferred environmental interpretations.

---

## 6. The Generalized Timeline

The temporal visualization system is one of the central components of Dancing with SAR.

Instead of presenting satellite observations independently, the timeline organizes them into a sequence of observations of the same geographical region.

### Capabilities

- Display available acquisition dates.
- Navigate between observations.
- Play observations chronologically.
- Pause and inspect individual dates.
- Compare two selected acquisition dates.
- Synchronize timeline selection with the Earth visualization.
- Update spatial layers according to the selected observation.

### Example

Consider a flood-monitoring study area.

| Observation | Timeline Event |
|---|---|
| \(T_1\) | Before flooding |
| \(T_2\) | Early flood development |
| \(T_3\) | Maximum observed inundation |
| \(T_4\) | Receding water |
| \(T_5\) | Post-event observation |

As the timeline progresses, the corresponding radar layer changes.

The user can visually follow the evolution of the region rather than interpreting five unrelated satellite images.

The generalized timeline should remain independent of the underlying scientific domain so it can also support Avani's atmospheric observations.

---

## 7. Interactive Earth Visualization

Dancing with SAR uses an interactive Earth interface as the primary medium for exploring spatial observations.

The globe provides a common geographical reference for radar measurements and derived analytical layers.

### Primary Visualization Features

- Interactive 3D Earth.
- Geographic region selection.
- Spatial observation overlays.
- SAR raster visualization.
- Temporal layer switching.
- Before-and-after comparison.
- Change-detection visualization.
- Observation metadata inspection.

### Spatial Representation

SAR observations are not necessarily point-based measurements.

Many products represent spatially continuous raster data or georeferenced image footprints.

Consequently, TerraTrace must preserve the spatial geometry and coordinate reference of the selected product rather than treating every radar measurement as an independent latitude-longitude point.

Where appropriate, observations can be mapped onto the Earth visualization using georeferenced raster textures or tiled spatial layers.

The existing globe infrastructure from Avani can serve as the visualization foundation, provided its rendering pipeline supports the spatial data representation required by the selected SAR products.

---

## 8. System Architecture

The proposed architecture separates the shared application infrastructure from the scientific processing pipeline.

```text
                   DANCING WITH SAR
                          |
                 Earth Twin Engine
                          |
       +------------------+------------------+
       |                  |                  |
  Spatial System    Temporal System    Visualization
       |                  |                  |
       +------------------+------------------+
                          |
                   TerraTrace
                          |
                 SAR Data Adapter
                          |
                  Data Preparation
                          |
              Spatial Registration
                          |
              Observation Management
                          |
                 SAR Processing
                          |
               Change Detection
                          |
               Analytical Layers
                          |
               Earth Visualization
                          |
                 Timeline Playback
```

### 8.1 Presentation Layer

Responsible for user interaction and visualization.

Components:

- Interactive Earth.
- Timeline controls.
- Study area selection.
- Layer management.
- Observation comparison.
- Metadata panels.

### 8.2 Application Runtime

Coordinates application workflows and communication between subsystems.

Responsibilities:

- Managing observation requests.
- Coordinating data ingestion.
- Managing spatial and temporal state.
- Updating visualization layers.
- Handling user interactions.

### 8.3 Scientific Processing Layer

Contains SAR-specific processing and analytical operations.

Responsibilities:

- Product interpretation.
- Backscatter preparation.
- Spatial alignment.
- Temporal comparison.
- Change detection.
- Analytical layer generation.

### 8.4 Data Layer

Responsible for retrieving and preparing external observations.

Potential data sources:

- NASA-ISRO NISAR data products.
- NASA Earthdata services.
- Alaska Satellite Facility DAAC resources, where applicable.
- Supplemental geographic and environmental datasets.

Data adapters should isolate external product formats from the shared application interfaces.

---

## 9. Data Pipeline

The SAR data pipeline transforms externally supplied radar observations into visualization-ready spatial layers.

```text
        NISAR DATA PRODUCTS
                 |
                 v
          Data Acquisition
                 |
                 v
          Product Inspection
                 |
                 v
          Data Preparation
                 |
                 v
       Spatial Reference Handling
                 |
                 v
         Temporal Organization
                 |
                 v
          SAR Measurements
                 |
                 v
        Scientific Processing
                 |
                 v
        Change Detection
                 |
                 v
        Visualization Layers
                 |
                 v
          Interactive Earth
```

### Data Preparation Considerations

The exact processing requirements depend on the selected NISAR product.

Potential requirements include:

- Product metadata inspection.
- Coordinate reference interpretation.
- Georeferencing.
- Radiometric calibration.
- Noise handling.
- Terrain correction.
- Spatial alignment.
- Raster preparation.
- Measurement normalization.

Not every operation is required for every product. Existing calibrated and geocoded products should be preferred where they satisfy the intended analysis.

### Data Formats

The application should select its supported formats based on the actual NISAR products supplied by the challenge.

Potential formats and representations include:

- HDF5-based scientific products.
- GeoTIFF and other geospatial raster representations.
- NetCDF where provided.
- Geospatial metadata and auxiliary files.

The prototype should support the specific product used in its demonstration rather than attempting to implement every possible NISAR product format.

---

## 10. Scientific Applications

The architecture is intended to support several types of Earth surface monitoring.

### Flood Monitoring

SAR can help identify inundated regions because open water often produces a distinct radar response.

Potential visualizations:

- Flood extent.
- Before-and-after comparisons.
- Inundation evolution.
- Receding water patterns.

### Wetland Monitoring

Observe changes in wetland extent and seasonal surface conditions.

### Forest Disturbance

Investigate changes in radar backscatter associated with forest structure and disturbance.

### Agricultural Monitoring

Explore changes in agricultural landscapes and radar responses associated with surface and vegetation conditions.

### Surface Deformation

Where appropriate NISAR interferometric products and processing are available, explore ground deformation associated with geological processes.

These applications represent future extensions. The initial implementation should prioritize one study area and one scientific phenomenon.

---

## 11. Relationship with Avani

Dancing with SAR is designed as an extension of the geospatial and spatiotemporal architecture explored in Avani.

Avani originally addressed the visualization and analysis of atmospheric observations for extreme-weather anomaly tracking.

Its architecture already explores several capabilities relevant to Dancing with SAR:

- Geographic positioning.
- Spatial data organization.
- Time-dependent observations.
- Interactive Earth visualization.
- Temporal navigation.
- Spatial visualization layers.

These capabilities provide a starting point for the new project.

### Reusable Components

| Existing Avani Capability | Dancing with SAR Application |
|---|---|
| Earth visualization | SAR observation visualization |
| Geographic positioning | Radar spatial registration |
| Timeline | SAR acquisition timeline |
| Spatial layer management | Radar and change-detection layers |
| Temporal data organization | Chronological SAR observations |
| Visualization controls | Polarization and observation controls |

### Components Requiring Extension

| Component | Required Development |
|---|---|
| Data ingestion | NISAR-specific adapter |
| Data normalization | SAR product interpretation |
| Scientific processing | Backscatter and other product-specific processing |
| Change analysis | Temporal SAR comparison |
| Layer rendering | Georeferenced SAR raster support |
| Metadata management | Radar acquisition metadata |

The intention is to reuse the underlying engineering work without making the new application dependent on Avani's weather-specific scientific logic.

---

## 12. Technology and Implementation Strategy

The implementation should prioritize technologies already used in the existing Avani codebase.

The initial strategy is to preserve its established frontend, backend, and globe visualization rather than introducing a completely new technology stack during the hackathon.

### Existing Infrastructure

Reuse where verified:

- Existing frontend application.
- Existing backend runtime.
- Earth visualization and rendering.
- Geographic coordinate handling.
- Generalized timeline.
- Spatial layer infrastructure.

### New Scientific Components

Implement:

- NISAR data adapter.
- SAR observation model.
- Product metadata interpretation.
- Raster preparation.
- Temporal comparison.
- Change-detection workflow.
- SAR-specific visualization layers.

### Architectural Principle

**Reuse the engine. Replace the scientific domain logic. Extend the visualization.**

---

## 13. Two-Day Hackathon Implementation Plan

The primary objective is to produce a functional, demonstrable prototype within the available event period.

The project should not attempt to implement every capability described in the long-term architecture.

### Phase 1 — Foundation and Data Acquisition

- Inspect Avani's existing architecture.
- Identify reusable globe, timeline, and spatial-layer components.
- Review the NISAR resources supplied by the challenge.
- Select one study area.
- Select one suitable SAR product.
- Obtain and inspect the actual dataset.

**Deliverable:** A verified SAR dataset and a working integration plan.

### Phase 2 — SAR Data Integration

- Implement the minimum required NISAR data adapter.
- Extract relevant measurements and metadata.
- Preserve geospatial information.
- Organize observations by acquisition date.
- Prepare visualization-ready raster layers.

**Deliverable:** SAR observations available inside the application.

### Phase 3 — Temporal Visualization

- Connect SAR observations to the generalized timeline.
- Display observations on the Earth.
- Implement date selection.
- Add chronological playback.
- Implement before-and-after comparison.

**Deliverable:** A functioning spatiotemporal SAR visualization.

### Phase 4 — Change Detection

- Implement a suitable comparison method for the chosen product.
- Generate a change-detection layer.
- Visualize the observed differences.
- Add basic contextual interpretation.

**Deliverable:** An interpretable surface-change visualization.

### Phase 5 — Demonstration and Documentation

- Prepare a focused study-area demonstration.
- Explain the data source and methodology.
- Demonstrate the timeline.
- Show the observed changes.
- Document limitations and future extensions.

**Deliverable:** A complete hackathon prototype and presentation.

---

## 14. Minimum Viable Product (MVP)

The MVP should demonstrate one complete scientific workflow.

### Required Features

- [ ] Interactive Earth visualization.
- [ ] One selected study area.
- [ ] At least two suitable SAR observations from different acquisition dates.
- [ ] NISAR data ingestion.
- [ ] Geospatially correct SAR visualization.
- [ ] Acquisition-date timeline.
- [ ] Before-and-after comparison.
- [ ] One scientifically appropriate change-detection visualization.
- [ ] Basic explanation of the observed changes.
- [ ] Source and processing information.

### Stretch Goals

- [ ] Multiple polarization channels.
- [ ] Additional study areas.
- [ ] Temporal animation.
- [ ] Multiple analytical layers.
- [ ] Supplemental optical imagery.
- [ ] Wetland and forest monitoring.
- [ ] Advanced interferometric deformation analysis.
- [ ] Additional Earth-observation data sources.

The MVP takes priority over the stretch goals.

---

## 15. Scientific Integrity and Limitations

Radar measurements are not direct labels of environmental phenomena.

A change in backscatter does not automatically mean flooding, deforestation, or soil-moisture change.

Interpretation must account for:

- Radar polarization.
- Acquisition geometry.
- Surface roughness.
- Dielectric properties.
- Vegetation structure.
- Temporal and seasonal variation.
- Spatial resolution.
- Calibration and processing conditions.

For example, a flood-monitoring workflow must distinguish potential inundation signatures from other changes that could affect radar backscatter.

Similarly, ground deformation analysis requires suitable interferometric observations and appropriate processing. A simple difference between two backscatter images is not an InSAR deformation measurement.

The application should communicate the distinction between measured observations, analytical results, and scientific hypotheses.

---

## 16. Expected Impact

Dancing with SAR aims to make radar-based Earth observation more accessible and understandable.

Potential beneficiaries include:

- Earth scientists and remote-sensing researchers.
- Disaster-management authorities.
- Environmental monitoring organizations.
- Agricultural researchers.
- Resource managers.
- Educators and students.
- Communities affected by environmental change.

By combining spatial visualization with temporal analysis, the platform can help users understand not only where environmental changes occur, but also how they evolve.

---

## 17. Future Direction

Dancing with SAR is the first planned scientific application built upon the Earth Twin Engine's reusable geospatial and temporal foundation.

Future development could extend the engine toward a broader Earth observation environment integrating multiple complementary data sources.

Potential extensions include:

- Optical satellite imagery.
- Atmospheric observations.
- Land-surface measurements.
- Vegetation indices.
- Hydrological observations.
- Additional radar missions.
- Multi-sensor data fusion.
- Long-term environmental trend analysis.

The longer-term goal is to provide a common environment in which different observations of Earth can be spatially and temporally connected.

---

## 18. Project Vision

Earth is continuously changing.

Some changes unfold over hours, others over seasons, decades, or geological timescales. Many remain difficult to observe directly, especially across large geographical regions.

Radar remote sensing provides a powerful way to observe these transformations.

Dancing with SAR seeks to turn those observations into a visual and interactive experience, connecting geographical space with time and scientific interpretation.

Through the Earth Twin Engine and its TerraTrace subsystem, the project aims to make Earth's changing surface easier to explore, understand, and communicate.

**Because Earth's surface is never still. It is always dancing.**

---

## 19. Acknowledgements and Data Sources

- NASA-ISRO Synthetic Aperture Radar (NISAR) Mission.
- NASA Earth Science.
- NASA Earthdata.
- Alaska Satellite Facility Distributed Active Archive Center (ASF DAAC), where applicable.
- NASA Space Apps Challenge.

All datasets and third-party resources will be used according to their respective access conditions, attribution requirements, and data-use policies.

---

**Project:** Dancing with SAR  
**Engine:** Earth Twin Engine (ETE)  
**Subsystem:** TerraTrace  
**Challenge:** NASA Space Apps Challenge — Dancing with SAR  
**Status:** Hackathon Prototype — In Development