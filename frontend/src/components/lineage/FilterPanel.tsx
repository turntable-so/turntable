import React, { useContext } from 'react';
import { Panel } from 'reactflow';
import { ConnectionTypeLabel, getLabelName } from './ColumnConnectionEdge';
import { LineageViewContext } from './LineageView';
import { CONNECTION_TYPES } from './constants';
import { Filter, X } from 'lucide-react';
import { Label } from "../ui/label"
import { RadioGroup, RadioGroupItem } from "../ui/radio-group"
import { Button } from '../ui/button';

export function FilterPanel() {
  const { isFilterOpen, toggleFilter, lineageOptions, setLineageOptionsAndRefetch } =
    useContext(LineageViewContext);

  if (!isFilterOpen) {
    return (
      <Panel position="top-right">
        <div
          className="
          bg-white opacity-70
          border-2 border-gray-300
              p-1.5
              rounded-lg
              flex items-center gap-1.5
              cursor-pointer
              "
          onClick={toggleFilter}
        >
          <div className='flex items-center text-xs text-muted-foreground uppercase  font-medium'>
            <Filter className={`mr-1 size-4 ${lineageOptions.lineageType === 'direct_only' ? 'text-blue-500' : ''}`} />
            {lineageOptions.lineageType === 'direct_only' ? (
              <div>
                Direct
              </div>
            ) : (
              <div>
                All
              </div>
            )}
          </div>
        </div>
      </Panel>
    );
  }

  return (
    <Panel position="top-right">
      <div
        className="
          w-64
          p-1.5
          rounded-lg
          bg-white"
      >
        <div className="flex justify-between items-center">
          <div className="w-full flex gap-1.5 items-center justify-center mb-1">

            <div className="flex flex-grow justify-between text-xs font-semibold text-muted-foreground dark:text-gray-300">
              <div className='px-1 flex items-center'>
                <Filter size='16' className='mr-1' />
                Connection Type Filter
              </div>

              <X size='20' onClick={toggleFilter} className='bg-gray-200 rounded-md m-0.5 text-muted-foreground opacity-70 hover:opacity-100 cursor-pointer' />
            </div>
          </div>
        </div>
        <div>
          <RadioGroup defaultValue={lineageOptions.lineageType} onValueChange={(t: 'all' | 'direct_only') => setLineageOptionsAndRefetch({
            ...lineageOptions, lineageType: t
          })} className='p-1 text-muted-foreground text-xs space-y-2'>
            <div className='flex justify-between border rounded-lg py-2 px-2'>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="all" id="all" />
                <Label htmlFor="all">All</Label>
              </div>
              <div className='flex flex-col mr-2'>
                {CONNECTION_TYPES.map(type => (
                  <div key={type} className='flex space-x-2'>
                    <ConnectionTypeLabel key={type} type={type} />
                    <div>{getLabelName(type)}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className='flex justify-between border rounded-lg py-2 px-2'>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="direct_only" id="direct_only" />
                <Label htmlFor="direct_only">Direct Only</Label>
              </div>
              <div className='flex flex-col mr-2'>
                <div className='flex space-x-2'>
                  <ConnectionTypeLabel type={'as_is'} />
                  <div>{getLabelName('as_is')}</div>
                </div>
                <div className='flex space-x-2'>
                  <ConnectionTypeLabel type={'transform'} />
                  <div>{getLabelName('transform')}</div>
                </div>
              </div>
            </div>
          </RadioGroup>
        </div>
      </div>
    </Panel>
  );
}
