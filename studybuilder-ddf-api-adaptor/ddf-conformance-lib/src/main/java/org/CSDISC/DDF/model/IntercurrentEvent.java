package org.CSDISC.DDF.model;

/** An event(s) occurring after treatment initiation that affects either the interpretation or the existence of
 * the measurements associated with the clinical question of interest. (ICH E9 Addendum on Estimands)
 * @author Chris Upkes
 */

public class IntercurrentEvent {

    private final String intercurrentEventId;
    // The literal identifier (i.e., distinctive designation) of the intercurrent event.
    private String intercurrentEventName;
    // The textual representation of the intercurrent event.
    private String intercurrentEventDescription;
    // A textual description of the planned strategy to manage and/or mitigate intercurrent events.
    private String intercurrentEventStrategy;


    public IntercurrentEvent(String intercurrentEventId) {
        this.intercurrentEventId = intercurrentEventId;
    }

    public String getIntercurrentEventId() {
        return intercurrentEventId;
    }

    public String getIntercurrentEventName() {
        return intercurrentEventName;
    }

    public void setIntercurrentEventName(String intercurrentEventName) {
        this.intercurrentEventName = intercurrentEventName;
    }

    public String getIntercurrentEventDescription() {
        return intercurrentEventDescription;
    }

    public void setIntercurrentEventDescription(String intercurrentEventDescription) {
        this.intercurrentEventDescription = intercurrentEventDescription;
    }

    public String getIntercurrentEventStrategy() {
        return intercurrentEventStrategy;
    }

    public void setIntercurrentEventStrategy(String intercurrentEventStrategy) {
        this.intercurrentEventStrategy = intercurrentEventStrategy;
    }

}
