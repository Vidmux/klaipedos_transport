
<img width="710" height="439" alt="image" src="https://github.com/user-attachments/assets/e6e49197-50aa-480b-a106-c5f3c8d4e6fe" />


## Klaipėdos viešojo transporto integracija

Ši integracija leidžia stebėti Klaipėdos autobusų judėjimą Home Assistant.  

**Įdiegimas:**
1. Įdiekite per **HACS** auto-entities
2. Įdiekite per **HACS** https://github.com/Vidmux/klaipedos_transport/
3. Po įdiegimo pridėkite prie **Devices ant integrations**: Klaipėdos viešasis transportas
4. Laukelye: **route** įrašote maršruto numerį pvz: 4G, 14 ir t.t.
5. Jei yra noras turėti kelis maršrutus 2 ir 3 punktus reikia pakartoti.
6. Pagal maršrutą automatiškai bus sukuriami `device_tracker` objektai.

**Pavyzdinė `Lovelace` kortelė:**

```yaml
type: custom:auto-entities
card:
  type: map
  title: "3G / 4G autobusai mieste"
  hours_to_show: 0
  dark_mode: false
filter:
  include:
    - entity_id: device_tracker.klp_4g_*
      options:
        name: "4G"
    - entity_id: device_tracker.klp_3g_*
      options:
        name: "3G"
show_empty: true
sort:
  method: friendly_name
