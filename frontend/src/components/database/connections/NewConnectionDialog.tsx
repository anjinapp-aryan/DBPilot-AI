"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const connectionSchema = z.object({
  name: z.string().min(1, "Give this connection a name"),
  host: z.string().min(1, "Host is required"),
  port: z.coerce.number().int().min(1).max(65535),
  database: z.string().min(1, "Database name is required"),
  username: z.string().min(1, "Username is required"),
});

type ConnectionFormInput = z.input<typeof connectionSchema>;
type ConnectionFormOutput = z.output<typeof connectionSchema>;

export function NewConnectionDialog() {
  const [open, setOpen] = useState(false);
  const {
    register,
    formState: { errors },
  } = useForm<ConnectionFormInput, unknown, ConnectionFormOutput>({
    resolver: zodResolver(connectionSchema),
    defaultValues: { port: 5432 },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="gap-1.5">
          <Plus className="size-4" /> New connection
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New database connection</DialogTitle>
          <DialogDescription>
            This form validates locally so you can preview the flow — saving connections isn&apos;t
            wired up to the backend yet.
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="conn-name">Connection name</Label>
            <Input id="conn-name" placeholder="Production Postgres" {...register("name")} />
            {errors.name && <p className="text-xs text-danger">{errors.name.message}</p>}
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2 space-y-1.5">
              <Label htmlFor="conn-host">Host</Label>
              <Input id="conn-host" placeholder="db.example.com" {...register("host")} />
              {errors.host && <p className="text-xs text-danger">{errors.host.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="conn-port">Port</Label>
              <Input id="conn-port" type="number" {...register("port")} />
              {errors.port && <p className="text-xs text-danger">{errors.port.message}</p>}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="conn-database">Database</Label>
            <Input id="conn-database" placeholder="app_production" {...register("database")} />
            {errors.database && <p className="text-xs text-danger">{errors.database.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="conn-username">Username</Label>
            <Input id="conn-username" placeholder="readonly_user" {...register("username")} />
            {errors.username && <p className="text-xs text-danger">{errors.username.message}</p>}
          </div>
        </form>

        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Tooltip>
            <TooltipTrigger asChild>
              <span tabIndex={0}>
                <Button disabled>Save connection</Button>
              </span>
            </TooltipTrigger>
            <TooltipContent>
              Saving connections isn&apos;t available yet — no backend endpoint exists.
            </TooltipContent>
          </Tooltip>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
