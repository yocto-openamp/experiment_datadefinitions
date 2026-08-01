# Broadcast

## Core mechanisms used/not used

* pydantic: The values of the pydantic object should NEVER be assigned.


## Observer: All assignements are done as follows

**Roles**

  * somewhere: For example user on web or service interface.
  * M7: The M7 is the source of truth

**Flow**

* somewhere: set_request(path, value)
  * This will assign the pydantic element and possibly trigger an exception
  * If exception happened:
    * Error message to the user
    * Stop
  * This will set the state in the hierarchy to 'IN_TRANSITION'
  * notify-broadcast
  * send set_request to M7
* M7: set_value(path, value)
  * This will assign the pydantic element and possibly trigger an exception
    * If exception happened:
      * Fatal message to the user (this should never happen)
      * Stop
    * This will set the state in the hierarchy to 'KNOWN'
    * notify-broadcast

**Side effects**

* Avoid round trip loops: If changing A triggers an update to B and this again triggers an update to A.
  How to avoid this? The gui elements only trigger an update from a use interaction. Updates from the observer do update, but the trigger is swallowed. 

## Developer guideline

* You may access all values in the pydantic models.
* However, you should NOT set the values although this is possible. Instead use set_request(path, value)
