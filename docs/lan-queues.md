# LAN Queues

**A LAN queue is a local network queue that multiple 3D printers print from.**

!!! Important

    This feature is only available in `v2.0.0` or higher.

It's not unusual to have multiple 3D printers - in home workshops, in the prototyping industry, and even for 3D printing services (e.g. Shapeways) and manufacturers that manage hundreds/thousands of them.

Continuous Print provides a single, local queue by default - managed by a single printer with a single instance of OctoPrint. But by adding LAN queues, multiple printers can coordinate together over the network to print jobs from the same queue(s).

!!! Warning

    This feature is not yet proven. If you encounter problems, please read this guide thoroughly before [creating an issue](https://github.com/smartin015/continuousprint/issues/new/choose) if you're unable to resolve them.

!!! Danger

    LAN queues are intended for trusted, local (LAN) networks only - not for cross-network (WAN) use cases. Using LAN queues across networks is insecure and strongly discouraged.

## Behavior

### LAN Queues manage Jobs, not Sets/Files

Queues operate at the level of a Job (see [Sets and Jobs](/advanced-queuing/#sets-and-jobs) for disambiguation). All work described by the job will be completed by the printer which acquires it. In other words, **the work within a job will not be distributed across printers**. This is to ensure compatability with future work to support WAN / decentralized network printing, ensuring that all prints of any job are guaranteed to end up in the same physical location.

### Queue Strategies

When a printer is done with its job, it will choose the next one based on whichever strategy is configured for the queue it's printing from. There is currently only one strategy:

*  **In-Order** prints linearly down the queue from top to bottom, one job at a time.

In the future, you will be able to customize how your printer works on the queue, e.g. choosing jobs in a way which avoids excessive filament changes and other manual actions.

The overall strategy *between* queues is currently in-order, i.e. all prints in the topmost queue will be executed before moving onto the next queue, and so on. This will eventually change to allow a top-level strategy which dictates which queue to print from.

### GCODE Limitations

3D print slicers generate a `*.gcode` file for a particular make and model of 3D printer - running that file on a different printer than the one for which it was sliced would likely damage that printer (or maybe just fail to print properly).

This can be mitigated in one of two ways:

1. Use exactly the same make and model of printer for all members of the LAN queue
2. Configure the correct [profiles](/printer-profiles) for all Sets so that each type of printer has its own compatible `*.gcode` files to fully print the job.

## Setup

By default, no LAN queues are configured and all prints are local to the specific instance of Octoprint.

**You will need a working instance of OctoPrint (with the Continuous Print plugin installed) for every printer you wish to have join the queue.**

## Add a LAN queue

1. Open OctoPrint's settings page
2. Click through to Continuous Print
3. Click the Queues button to go to the queue settings page.
4. Click the "Add Queue" button to add a new LAN queue.
5. Fill in the inputs, but keep in mind:
    * Each queue must have a unique name (which cannot be `local` and `archive` - these are reserved)
    * Hostname:Port must be of the form `hostname:port` (e.g. `0.0.0.0:6789`, `localhost:5001`, `myhostname:9007`)
        * A hostname of `localhost` will only connect to other OctoPrint instances on the same host. If you're unsure what to specify here, try `0.0.0.0` which [binds to all IP addresses on the host](https://en.wikipedia.org/wiki/0.0.0.0).
    * Access control may be a factor if you're using a port number below 1024 (see [privileged ports](https://www.w3.org/Daemon/User/Installation/PrivilegedPorts.html))
    * You may experience silent failures if you specify a port that's already in use by another process.
    * All LAN queues are only visible to other devices on the same network, unless you've taken steps to expose ports (NOT recommended).
6. When you've finished configuring your queues, click `Save`.

If everything is working properly, you'll see the changes reflected in the queues on the Continuous Print tab with the queue(s) you added. It will show no other peers connected to it, but that's because we still have to set them up. Complete steps 1-6 for all remaining printers, and you should see them as peers when you look at the header of the queue.

## Submit a job

Submitting a job is as simple as dragging it from the "local" queue to your LAN queue. After confirming that you wish to submit your job, the job will disappear from the local queue and show up on the LAN queue.

!!! Warning

    Currently, LAN queue submission is somewhat destructive - the job cannot be modified or reverted once it's submitted, only deleted.

    If you have a very complex job to submit, consider [saving it](/gjob-files) before submission so you have a backup.

## Cancel a job

1. Click the checkbox next to the job in your LAN queue.
1. Click the trash can icon that appears.

The job will disappear from the LAN queue and no longer be printed. Note that a job may not be deleted if a printer is actively printing it.
