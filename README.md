# Group Projects In Aerial Robotics
*MSc Aerial Robotics (TB2)*


## Overview

Advancements in aerial robotics are opening new possibilities for **wildlife monitoring and conservation efforts**. 
This project explores the development of an **autonomous drone-based system** designed to both 
**monitor zebra and rhinoceros populations**, as well as **look after them** with minimal ecological disturbance. 

Operating within the **Fenswood Conservancy**, the system integrates 
**image recognition, precision navigation, and automated flight control** using 
**AI and Computer Vision methods** to perform a detailed census of zebra populations while ensuring 
safe and ethical interaction with wildlife. Additionally, a specialized **sensor deployment mechanism** 
enables the UAV to deliver critical monitoring devices in proximity to designated locations, supporting 
long-term ecological data collection.  

This initiative is part of a broader effort to **develop robust, field-ready aerial systems** for conservation 
applications. By combining advanced drone technology with **intelligent automation**, the project aims to 
contribute meaningful innovations to the field of **remote ecological monitoring**.  


## Setup

Install Dependencies:
```
pip install --exists-action=i -r dependencies.txt
```


## Requirements

| Requirement ID | Requirement Description | Note |
|----------------|------------------------|--------|
| **R01** | The drone shall only fly within the Flight Area. | 1 |
| **R02** | The drone shall not fly over the Sensitive Area. | 1 |
| **R03** | The drone shall take off from a region within 5m of the Take-Off Location. | 1 |
| **R04** | The drone shall not exceed an altitude of 50m above Take-Off Location ground level. | 1 |
| **R05** | The drone shall survey the Survey Area and conduct a census of the zebra population. | 1 |
| **R06** | The drone shall land within 20 metres of a rhino and deploy the provided sensor package. |   |
| **R07** | The level of autonomy shall be determined and justified by the Company and approved by the Client. |   |
| **R08** | All interfaces (RC, Ground Station, and any others) shall include "Return to Home" (RTH) and "Motor Cutoff" commands and other appropriate failsafes. |  |
| **R09** | A count, latitude/longitudes, representative images of the zebra population, and the latitude/longitude and image(s) of the rhino shall be reported. Verification of R05 and R06 shall be via presentation and report appendix including relevant imagery, data, uncertainties, etc., with details agreed between Company and Client. |  |
| **R10** | The operation must have a designated Company Pilot, who will be responsible for compliant operation of the activity. The Company Pilot shall be supervised by a Flight Lab Safety Pilot, who shall have ultimate responsibility and absolute authority over all operations. Additional responsibilities may be allocated as required at Company and Lab discretion. |  |
| **R11** | All software and flight logs shall be delivered via a public GitHub repository linked from the Company Report, licensed under the MIT licence. |  |


> **1:** Coordinates are available in `AENGM0074.kml`. Areas will not be visibly marked in any field trials, but teams should report any excursions/incursions verbally during trials and in post-flight reports. Flight logs may be examined to verify compliance. Use of automatic geofences is advised.
