! Description:
! Definition of an output database.
module m_odb
    implicit none
    
    private
    public t_odb, new_odb
    
    type t_odb
        integer                    :: n_fields     ! number of scalar fields
        character(64), allocatable :: names(:)     ! names of values
        real,          allocatable :: values(:, :) ! values
    contains
        procedure :: set_field
        final     :: destructor
    end type
    
    interface new_odb
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Output database constructor.
    type(t_odb) function constructor(n_nodes, n_fields) result(this)
        integer, intent(in) :: n_nodes  ! number of mesh nodes
        integer, intent(in) :: n_fields ! number of scalar fields
        this%n_fields = n_fields
        allocate(this%names(this%n_fields))
        allocate(this%values(n_nodes, this%n_fields))
    end function
    
    ! Description:
    ! Output database destructor.
    subroutine destructor(this)
        type(t_odb), intent(inout) :: this
        if (allocated(this%names))  deallocate(this%names)
        if (allocated(this%values)) deallocate(this%values)
    end subroutine
    
    ! Description:
    ! Sets the field data.
    subroutine set_field(this, i, name, values)
        class(t_odb),  intent(inout) :: this
        integer,       intent(in)    :: i
        character(*),  intent(in)    :: name
        real,          intent(in)    :: values(:)
        this%names(i)     = name
        this%values(:, i) = values
    end subroutine
    
end module
